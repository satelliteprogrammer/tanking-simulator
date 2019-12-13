from enum import Enum


class Buff():

    def __init__(self, name, algebra, stamina, agility, strength, intellect, spirit):
        self.name = name
        self.algebra = algebra
        self.stamina = stamina
        self.agility = agility
        self.strength = strength
        self.intellect = intellect
        self.spirit = spirit


class Debuff():

    def __init__(self, name, algebra, stamina, agility, strength, intellect, spirit):
        self.name = name
        self.algebra = algebra
        self.stamina = stamina
        self.agility = agility
        self.strength = strength
        self.intellect = intellect
        self.spirit = spirit


class Order(Enum):
    LENIENT = 0
    HARSH = 1
    RANDOM = 2


def trange(stop):
    i = 0
    while i < stop:
        yield i
        i += 0.01
