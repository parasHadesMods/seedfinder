import pandas
import tkinter
import subprocess


class ButtonItem:
    def __init__(self, parent, item):
        self.button = tkinter.Button(
            parent, text=item["Text"], command=ButtonItem._mkcallback(item)
        )
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
        return self.option_menu.cget("state")

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
        menu = self.option_menu["menu"]
        menu.delete(0, "end")

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


ENEMIES = [
    "Swarmer",
    "HeavyMelee",
    "LightRanged",
    "PunchingBagUnit",
    ""
]
ROOMS = [
    "A_Combat01",
    "A_Combat02",
    "A_Combat03",
    "A_Combat04",
    "A_Combat05",
    "A_Combat06",
    "A_Combat07",
    "A_Combat08A",
    "A_Combat09",
    "A_Combat10",
    "A_Combat12",
    "A_Combat13",
    "A_Combat14",
    "A_Combat15",
    "A_Combat16",
    "A_Combat19",
    "A_Combat21",
    "A_Combat24",
]
RUN_REWARDS = [
    "ArtemisUpgrade",
    "AresUpgrade",
    "AthenaUpgrade",
    "DionysusUpgrade",
    "RoomRewardMaxHealthDrop",
    "RoomRewardMoneyDrop",
    "StackUpgrade",
]
META_REWARDS = ["LockKeyDrop", "RoomRewardMetaPointDrop"]


class Cell:
    def __init__(self):
        self.item = None

    def gets(self):
        return self.item

    def sets(self, item):
        self.item = item


C2_EXIT_REWARD = Cell()
C3_ROOM_NAME = Cell()
C3_WAVE_1_ENEMY_1 = Cell()
C3_WAVE_1_ENEMY_2 = Cell()
C3_WAVE_1_ENEMY_3 = Cell()
C3_WAVE_2_ENEMY_1 = Cell()
C3_WAVE_2_ENEMY_2 = Cell()
C3_WAVE_2_ENEMY_3 = Cell()
C3_WAVE_3_ENEMY_1 = Cell()
C3_WAVE_3_ENEMY_2 = Cell()
C3_WAVE_3_ENEMY_3 = Cell()
C3_EXIT_REWARD_1 = Cell()
C3_EXIT_REWARD_2 = Cell()
C3_DOOR_CHOSEN = Cell()
C4_ROOM_NAME = Cell()
C4_WAVE_1_ENEMY_1 = Cell()
C4_WAVE_1_ENEMY_2 = Cell()
C4_WAVE_1_ENEMY_3 = Cell()
C4_WAVE_2_ENEMY_1 = Cell()
C4_WAVE_2_ENEMY_2 = Cell()
C4_WAVE_2_ENEMY_3 = Cell()
C4_WAVE_3_ENEMY_1 = Cell()
C4_WAVE_3_ENEMY_2 = Cell()
C4_WAVE_3_ENEMY_3 = Cell()
C4_EXIT_REWARD_1 = Cell()
C4_EXIT_REWARD_2 = Cell()
C1_SEED = Cell()
C2_SEED = Cell()
C3_SEED = Cell()
C4_SEED = Cell()
PREDICTION = Cell()


def join_cells(*args):
    non_null_args = [x.gets() for x in args if x.gets()]
    return "+".join(sorted(non_null_args))


RAW_DATA = None

def get_seeds():
    data = RAW_DATA
    data = data[data["C2_Exit_Reward"] == C2_EXIT_REWARD.gets()]
    data = data[data["C3_Room_Name"] == C3_ROOM_NAME.gets()]
    data = data[
        data["C3_Exit_Rewards"] == join_cells(C3_EXIT_REWARD_1, C3_EXIT_REWARD_2)
    ]
    wave_1 = join_cells(C3_WAVE_1_ENEMY_1, C3_WAVE_1_ENEMY_2, C3_WAVE_1_ENEMY_3)
    wave_2 = join_cells(C3_WAVE_2_ENEMY_1, C3_WAVE_2_ENEMY_2, C3_WAVE_2_ENEMY_3)
    wave_3 = join_cells(C3_WAVE_3_ENEMY_1, C3_WAVE_3_ENEMY_2, C3_WAVE_3_ENEMY_3)
    data = data[data["C3_Wave_1"] == wave_1]
    if wave_2:
        data = data[data["C3_Wave_2"] == wave_2]
    else:
        data = data[data["C3_Wave_2"].isna()]
    if wave_3:
        data = data[data["C3_Wave_3"] == wave_3]
    else:
        data = data[data["C3_Wave_3"].isna()]
    data = data[data["C3_Exit_Chosen"] == C3_DOOR_CHOSEN.gets()]
    data = data[data["C4_Room_Name"] == C4_ROOM_NAME.gets()]
    data = data[
        data["C4_Exit_Rewards"] == join_cells(C4_EXIT_REWARD_1, C4_EXIT_REWARD_2)
    ]
    wave_1 = join_cells(C4_WAVE_1_ENEMY_1, C4_WAVE_1_ENEMY_2, C4_WAVE_1_ENEMY_3)
    wave_2 = join_cells(C4_WAVE_2_ENEMY_1, C4_WAVE_2_ENEMY_2, C4_WAVE_2_ENEMY_3)
    wave_3 = join_cells(C4_WAVE_3_ENEMY_1, C4_WAVE_3_ENEMY_2, C4_WAVE_3_ENEMY_3)
    data = data[data["C4_Wave_1"] == wave_1]
    if wave_2:
        data = data[data["C4_Wave_2"] == wave_2]
    else:
        data = data[data["C4_Wave_2"].isna()]
    if wave_3:
        data = data[data["C4_Wave_3"] == wave_3]
    else:
        data = data[data["C4_Wave_3"].isna()]
    try:
        C1_SEED.sets(data["C1_Seed"].iloc[0])
        C2_SEED.sets(data["C2_Seed"].iloc[0])
        C3_SEED.sets(data["C3_Seed"].iloc[0])
        C4_SEED.sets(data["C4_Seed"].iloc[0])
    except IndexError:
        C4_SEED.sets("Unknown")

def predict():
    data = RAW_DATA
    data = data[(data["C1_Seed"] == C1_SEED.gets()) &
                (data["C2_Seed"] == C2_SEED.gets()) &
                (data["C3_Seed"] == C3_SEED.gets()) &
                (data["C4_Seed"] == C4_SEED.gets())]
    with open("run_for_prediction.json", "w") as j:
        j.write(data.iloc[0].to_json())
    result = subprocess.run("""cd ../routefinder && ./target/release/routefinder -s ~/legendary/Hades/Content/Scripts -f FreshFile.sav FreshFilePredict.lua""", shell=True, capture_output=True)
    PREDICTION.sets(result.stdout)

ELEMENTS = [
    {
        "Type": "Combo",
        "Prompt": "C2 Exit Reward",
        "GetCurrent": C2_EXIT_REWARD.gets,
        "OnSelect": C2_EXIT_REWARD.sets,
        "GetOptions": lambda: META_REWARDS,
    },
    {
        "Type": "Combo",
        "Prompt": "C3 Room Name",
        "GetCurrent": C3_ROOM_NAME.gets,
        "OnSelect": C3_ROOM_NAME.sets,
        "GetOptions": lambda: ROOMS if C2_EXIT_REWARD.gets() else [],
    },
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "Wave 1 Enemy",
        "GetCurrent": C3_WAVE_1_ENEMY_1.gets,
        "OnSelect": C3_WAVE_1_ENEMY_1.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 1 Enemy",
        "GetCurrent": C3_WAVE_1_ENEMY_2.gets,
        "OnSelect": C3_WAVE_1_ENEMY_2.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 1 Enemy",
        "GetCurrent": C3_WAVE_1_ENEMY_3.gets,
        "OnSelect": C3_WAVE_1_ENEMY_3.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "Wave 2 Enemy",
        "GetCurrent": C3_WAVE_2_ENEMY_1.gets,
        "OnSelect": C3_WAVE_2_ENEMY_1.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 2 Enemy",
        "GetCurrent": C3_WAVE_2_ENEMY_2.gets,
        "OnSelect": C3_WAVE_2_ENEMY_2.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 2 Enemy",
        "GetCurrent": C3_WAVE_2_ENEMY_3.gets,
        "OnSelect": C3_WAVE_2_ENEMY_3.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "Wave 3 Enemy",
        "GetCurrent": C3_WAVE_3_ENEMY_1.gets,
        "OnSelect": C3_WAVE_3_ENEMY_1.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 3 Enemy",
        "GetCurrent": C3_WAVE_3_ENEMY_2.gets,
        "OnSelect": C3_WAVE_3_ENEMY_2.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 3 Enemy",
        "GetCurrent": C3_WAVE_3_ENEMY_3.gets,
        "OnSelect": C3_WAVE_3_ENEMY_3.sets,
        "GetOptions": lambda: ENEMIES if C3_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "C3 Exit Reward",
        "GetCurrent": C3_EXIT_REWARD_1.gets,
        "OnSelect": C3_EXIT_REWARD_1.sets,
        "GetOptions": lambda: RUN_REWARDS if C3_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "C3 Exit Reward",
        "GetCurrent": C3_EXIT_REWARD_2.gets,
        "OnSelect": C3_EXIT_REWARD_2.sets,
        "GetOptions": lambda: RUN_REWARDS if C3_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {
        "Type": "Combo",
        "Prompt": "Door Chosen",
        "GetCurrent": C3_DOOR_CHOSEN.gets,
        "OnSelect": C3_DOOR_CHOSEN.sets,
        "GetOptions": lambda: RUN_REWARDS
        if C3_EXIT_REWARD_1.gets() and C3_WAVE_1_ENEMY_1.gets()
        else [],
    },
    {
        "Type": "Combo",
        "Prompt": "C4 Room Name",
        "GetCurrent": C4_ROOM_NAME.gets,
        "OnSelect": C4_ROOM_NAME.sets,
        "GetOptions": lambda: ROOMS if C3_DOOR_CHOSEN.gets() else [],
    },
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "Wave 1 Enemy",
        "GetCurrent": C4_WAVE_1_ENEMY_1.gets,
        "OnSelect": C4_WAVE_1_ENEMY_1.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 1 Enemy",
        "GetCurrent": C4_WAVE_1_ENEMY_2.gets,
        "OnSelect": C4_WAVE_1_ENEMY_2.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 1 Enemy",
        "GetCurrent": C4_WAVE_1_ENEMY_3.gets,
        "OnSelect": C4_WAVE_1_ENEMY_3.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "Wave 2 Enemy",
        "GetCurrent": C4_WAVE_2_ENEMY_1.gets,
        "OnSelect": C4_WAVE_2_ENEMY_1.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 2 Enemy",
        "GetCurrent": C4_WAVE_2_ENEMY_2.gets,
        "OnSelect": C4_WAVE_2_ENEMY_2.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 2 Enemy",
        "GetCurrent": C4_WAVE_2_ENEMY_3.gets,
        "OnSelect": C4_WAVE_2_ENEMY_3.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "Wave 3 Enemy",
        "GetCurrent": C4_WAVE_3_ENEMY_1.gets,
        "OnSelect": C4_WAVE_3_ENEMY_1.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 3 Enemy",
        "GetCurrent": C4_WAVE_3_ENEMY_2.gets,
        "OnSelect": C4_WAVE_3_ENEMY_2.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "Wave 3 Enemy",
        "GetCurrent": C4_WAVE_3_ENEMY_3.gets,
        "OnSelect": C4_WAVE_3_ENEMY_3.sets,
        "GetOptions": lambda: ENEMIES if C4_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {"Type": "RowStart"},
    {
        "Type": "Combo",
        "Prompt": "C4 Exit Reward",
        "GetCurrent": C4_EXIT_REWARD_1.gets,
        "OnSelect": C4_EXIT_REWARD_1.sets,
        "GetOptions": lambda: META_REWARDS if C4_ROOM_NAME.gets() else [],
    },
    {
        "Type": "Combo",
        "Prompt": "C4 Exit Reward",
        "GetCurrent": C4_EXIT_REWARD_2.gets,
        "OnSelect": C4_EXIT_REWARD_2.sets,
        "GetOptions": lambda: META_REWARDS if C4_ROOM_NAME.gets() else [],
    },
    {"Type": "RowEnd"},
    {
        "Type": "Button",
        "Text": "Get Seed",
        "Predicate": lambda: C4_EXIT_REWARD_1.gets() and C4_WAVE_1_ENEMY_1.gets(),
        "Function": get_seeds,
    },
    {"Type": "Label", "GetCurrent": C4_SEED.gets},
    {
        "Type": "Button",
        "Text": "Predict",
        "Predicate": lambda: C4_SEED.gets() and C4_SEED.gets() != "Unknown",
        "Function": predict,
    },
    {"Type": "Label", "GetCurrent": PREDICTION.gets},
]

if __name__ == "__main__":
    with open("freshfile.csv") as f:
        RAW_DATA = pandas.read_csv(f)
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
            item["Refresh"] = lambda label=label, item=item: label.configure(
                text=item["GetCurrent"]()
            )
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
