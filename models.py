import dataclasses
import inspect
import json
from dataclasses import dataclass, field
from pathlib import Path

from typing import List, Union, NewType


@dataclass
class BaseModel:
    id: int = field(init=False, default=0)

    def __setitem__(self, key, value):
        setattr(self, key, value)


@dataclass
class ItemModel(BaseModel):
    _counter: int = field(init=False, repr=False, default=0)
    name: str
    damage: int = 5

    def __post_init__(self):
        ItemModel._counter += 1
        self.id = ItemModel._counter


@dataclass(order=True)
class MainCharModel(BaseModel):
    sort_index: int = field(init=False, repr=False)
    _counter: int = field(init=False, repr=False, default=0)
    current_item: ItemModel = field(init=False)
    name: str
    damage: int = 2
    hp: int = 10
    items: List[ItemModel] = field(default_factory=list)

    def __post_init__(self):
        self.sort_index = self.hp
        MainCharModel._counter += 1
        self.id = MainCharModel._counter

        if not len(self.items):
            self.current_item = ItemModel(name="Hand")
        else:
            self.current_item = self.items[0]


class DataModel:
    PATHS = {
        "items": Path.cwd() / 'data' / 'item.json',
        "mainchar": Path.cwd() / 'data' / 'mainchar.json'
    }

    def __init__(self):
        self.items = self.load_items()
        self.mainchar = self.load_mainchar()

    def load_items(self) -> List[ItemModel]:
        data = load_data_from_json_file(self.PATHS['items'])
        return create_dataclasses_from_json_data(ItemModel, data)

    def load_mainchar(self) -> MainCharModel:
        data = load_data_from_json_file(self.PATHS['mainchar'])
        mainchar_class = create_dataclasses_from_json_data(MainCharModel, data)
        return resolve_to_n_data(mainchar_class, self.items, ['current_item', 'items'])[0]


ModelUnion = NewType('ModelUnion', Union[ItemModel, MainCharModel])


def from_dict_to_dataclass(cls, data):
    return cls(
        **{
            key: (data[key] if val.default == val.empty else data.get(key, val.default))
            for key, val in inspect.signature(cls).parameters.items()
        }
    )


def load_data_from_json_file(path: Path) -> List[dict]:
    """loads the saved data"""

    with open(path, 'r') as fp:
        return json.load(fp)


def create_dataclasses_from_json_data(datacls: dataclass, data: List[dict]) -> List[ModelUnion]:
    """ returns a list of initialized dataclasses from json data"""
    return [from_dict_to_dataclass(datacls, data_row) for data_row in data]


def resolve_to_n_data(
        dataclasses_to_resolve: List[ModelUnion],
        resolve_classes: List[ModelUnion],
        field_names: list) -> List[ModelUnion]:
    """
    looks for field_names in dataclass and resolves them with data from resolve classes.
    this allows the creation of 1:n data that gets resolved here
    """
    for dataclass_to_resolve in dataclasses_to_resolve:
        for key, val in dataclasses.asdict(dataclass_to_resolve).items():
            if key in field_names:
                if isinstance(val, list):
                    resolve_list = []
                    for id in range(len(val)):
                        resolve_list.append([x for x in resolve_classes if x.id == val[id]])
                    dataclass_to_resolve[key] = resolve_list
                else:
                    dataclass_to_resolve[key] = [x for x in resolve_classes if x.id == val][0]
    return dataclasses_to_resolve
