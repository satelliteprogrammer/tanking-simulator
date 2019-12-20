from random import random, uniform
from statistics import mean
from units import Healer


class Heal:

    def __init__(self, base: tuple, cast: float, coefficient: float, healing, crit, healer: Healer):
        self.base = base
        self.cast = min(1.5, cast) / (1 + healer.haste/100)
        self.coefficient = coefficient
        self.increased_healing = healing
        self.crit = crit + healer.crit

        self.healer = healer

    def apply(self):
        heal = (uniform(self.base[0], self.base[1]) + self.coefficient * self.healer.bh) * (1 + self.increased_healing)
        roll = random() * 100
        if roll < self.crit:
            return heal * 1.5
        else:
            return heal

    def hps(self):
        heal = (mean(self.base) + self.coefficient * self.healer.bh) * (1 + self.increased_healing)

        return (heal * 1.5 * self.crit/100 + heal * (1 - self.crit/100))/self.cast
