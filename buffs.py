from utils import Stats


class Buff:
    @staticmethod
    def apply(stats: Stats):
        pass


class BoK(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.stamina *= 1.1
        stats.agility *= 1.1
        stats.strength *= 1.1


class Fortitude(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.stamina += 100


class MotW(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.stamina += 18.9
        stats.agility += 18.9
        stats.strength += 18.9
