from dataclasses import dataclass
from jinja2 import Environment
import random
import csv

@dataclass
class MessageEntry:
    message: str
    weight: int

class MessageProvider:
    entries: dict[str, list[MessageEntry]]

    def __init__(self) -> None:
        self.entries = {}
        self.env = Environment()

    @classmethod
    def from_csv(cls, path:str)->"MessageProvider":
        provider = cls()
        with open(path, "r") as f:
            reader = csv.reader(f, delimiter="|")
            next(reader)
            for row in reader:
                key = row[0]
                message = row[1]
                weight = int(row[2])
                provider.add(key, MessageEntry(message, weight))

        return provider

    @classmethod
    def from_gsheets(cls, url:str)->"MessageProvider":
        provider = cls()  
        # TODO
        return provider


    def add(self, key:str, entry:MessageEntry):
        if key in self.entries:
            self.entries[key].append(entry)
        else:
            self.entries[key] = [entry]

    def __call__(self, key:str, **kwargs) -> str:  

        if key not in self.entries:
            return f"Message-Key `{key}` is not defined!"

        entries = self.entries[key]
        entry_to_render = None
        if len(entries) == 1:
            entry_to_render=entries[0]
        else:
            weights = [entry.weight for entry in entries]
            entry_to_render = random.choices(entries, weights = weights, k=1)[0]

        return self.env.from_string(entry_to_render.message).render(**kwargs)

    