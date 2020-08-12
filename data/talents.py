from simulator.utils import Attributes


class Talent:
    @staticmethod
    def apply(stats: Attributes):
        pass


class CombatExpertise(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.stamina *= (1 + .02 * self.rank)
        stats.expertise += self.rank


class SacredDuty(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.stamina *= (1 + .03 * self.rank)


class Deflection(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.parry += self.rank


class RighteousFury(Talent):
    def __init__(self, rank):
        self.rank = rank

    @staticmethod
    def apply(stats: Attributes):
        pass


class PaladinShieldSpecialization(Talent):
    def __init__(self, rank):
        self.rank = rank

    @staticmethod
    def apply(stats: Attributes):
        pass


class WarriorShieldSpecialization(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.block += self.rank


class Anticipation(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.defense += self.rank * 4


class Defiance(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.expertise += 2 * self.rank


class ShieldMastery(Talent):
    def __init__(self, rank):
        self.rank = rank

    @staticmethod
    def apply(stats: Attributes):
        pass


class Vitality(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.stamina *= (1 + .01 * self.rank)
        stats.strength *= (1 + .02 * self.rank)


class Toughness(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Attributes):
        stats.armor *= (1 + .02 * self.rank)
