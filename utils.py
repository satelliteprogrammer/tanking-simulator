from dataclasses import dataclass
from enum import Enum


@dataclass(eq=False)
class Stats:
    __slots__ = 'stamina', 'agility', 'strength', 'defense', 'miss', 'dodge', 'parry', 'block', 'block_value', 'armor',\
                'hit', 'expertise'

    stamina: float
    agility: float
    strength: float
    defense: float
    miss: float
    dodge: float
    parry: float
    block: float
    block_value: int
    armor: int
    hit: int
    expertise: int


class Order(Enum):
    LENIENT = 0
    HARSH = 1
    RANDOM = 2


def trange(stop):
    i = 0
    while i < stop:
        yield i
        i += 0.01
