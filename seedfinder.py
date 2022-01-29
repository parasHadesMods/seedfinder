import json
import tkinter

class ButtonItem:
  def __init__(self, parent, item):
    self.button = tkinter.Button(parent, text=item["Text"],
      command=ButtonItem._mkcallback(item))
    if "Predicate" in item:
      self.predicate = item["Predicate"]
    else:
      self.predicate = lambda: True

  @staticmethod
  def _mkcallback(item):
    def callback():
      item["Function"]()
      refresh()
    return callback

  def refresh(self):
    if self.predicate():
      self.button.config(state=tkinter.NORMAL)
    else:
      self.button.config(state=tkinter.DISABLED)

class ComboItem:
  def __init__(self, parent, item):
    self.parent = parent
    self.item = item
    self.prompt = item["Prompt"]
    self.get_current = item["GetCurrent"]
    self.on_select = item["OnSelect"]
    self.get_options = item["GetOptions"]
    self.variable = tkinter.StringVar(parent)
    self.option_menu = tkinter.OptionMenu(parent, self.variable, None)
    self.option_menu.configure(state=tkinter.DISABLED)

  def state(self):
    return self.option_menu.cget('state')

  def _mkcallback(self, item):
    def callback():
      self.on_select(item)
      refresh()
    return callback

  def disable_option_menu_eventually(self):
    current_state = self.state()
    if current_state == tkinter.DISABLED:
      pass
    elif current_state == tkinter.NORMAL:
      self.option_menu.configure(state=tkinter.DISABLED)
    else:
      self.option_menu.after(20, lambda: self.disable_option_menu_eventually())

  def refresh(self):
    options = self.get_options()
    menu = self.option_menu['menu']
    menu.delete(0, 'end')

    if len(options) > 0:
      for text in options:
        menu.add_command(label=text, command=self._mkcallback(text))
      self.option_menu.configure(state=tkinter.NORMAL)
    else:
      self.disable_option_menu_eventually()

    selected = self.get_current()
    if selected:
      self.variable.set(selected)
    else:
      self.variable.set(self.prompt)

def refresh():
  for elem in ELEMENTS:
    if "Refresh" in elem:
      elem["Refresh"]()

ROOM_NAMES = [
  "A_Combat01",
  "A_Combat02",
  "A_Combat03",
  "A_Combat04",
  "A_Combat05",
  "A_Combat06",
  "A_Combat07",
  "A_Combat08A",
  "A_Combat08B",
  "A_Combat09",
  "A_Combat10",
  "A_Combat11",
  "A_Combat12",
  "A_Combat13",
  "A_Combat14",
  "A_Combat15",
  "A_Combat16",
  "A_Combat17",
  "A_Combat18",
  "A_Combat19",
  "A_Combat20",
  "A_Combat24"
]

class StringCell():
  def __init__(self):
    self.string = None
  def gets(self):
    return self.string
  def sets(self, string):
    self.string = string

C2_EXIT_REWARD = StringCell()
C3_ROOM_NAME = StringCell()
C3_EXIT_REWARD_1 = StringCell()
C3_EXIT_REWARD_2 = StringCell()

def get_seeds():
  with open("freshfile.json") as f:
    data = json.load(f)
    data = data[C2_EXIT_REWARD.gets()]
    data = data[C3_ROOM_NAME.gets()]
    print(data)

ELEMENTS = [
  { "Type": "Combo",
    "Prompt": "C2 Exit Reward",
    "GetCurrent": C2_EXIT_REWARD.gets,
    "OnSelect": C2_EXIT_REWARD.sets,
    "GetOptions": lambda: ["LockKeyDrop", "RoomRewardMetaPointDrop"] },
  { "Type": "Combo",
    "Prompt": "C3 Room Name",
    "GetCurrent": C3_ROOM_NAME.gets,
    "OnSelect": C3_ROOM_NAME.sets,
    "GetOptions": lambda: ROOM_NAMES if C2_EXIT_REWARD.gets() else [] },
  { "Type": "Button",
    "Text": "Get Seeds",
    "Predicate": lambda: C3_ROOM_NAME.gets(),
    "Function": get_seeds }
]

if __name__ == "__main__":
  window = tkinter.Tk()
  window.title("Fresh File Seed Finder")
  window.attributes("-topmost", True)

  SAVE_NAME_FIELD = tkinter.StringVar()

  parent = window
  row = 0
  column = 0
  window.grid_columnconfigure(0, weight=1)
  for item in ELEMENTS:
    to_pack = None
    if item["Type"] == "Combo":
      element = ComboItem(parent, item)
      to_pack = element.option_menu
      item["Refresh"] = element.refresh
    if item["Type"] == "Button":
      element = ButtonItem(parent, item)
      to_pack = element.button
      item["Refresh"] = element.refresh
    if item["Type"] == "Entry":
      entry = tkinter.Entry(parent, textvariable=SAVE_NAME_FIELD)
      to_pack = entry
    if item["Type"] == "Label":
      label = tkinter.Label(parent)
      to_pack = label
      item["Refresh"] = lambda label=label,item=item: label.configure(text=item["GetCurrent"]())
    if item["Type"] == "RowStart":
      parent = tkinter.Frame(parent)
      column = 0
      continue
    if item["Type"] == "RowEnd":
      to_pack = parent
      parent = window
    if parent == window:
      to_pack.grid(row=row, column=0, sticky="news")
      row += 1
    else:
      to_pack.grid(row=0, column=column, sticky="news")
      parent.grid_columnconfigure(column, weight=1, uniform="group1")
      column += 1

  refresh()

  window.mainloop()

