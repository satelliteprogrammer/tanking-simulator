from utils import Stats


class Talent:
    @staticmethod
    def apply(stats: Stats):
        pass


class CombatExpertise(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.stamina *= (1 + .02 * self.rank)
        stats.expertise += self.rank


class SacredDuty(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.stamina *= (1 + .03 * self.rank)


class Deflection(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.parry += self.rank


class RighteousFury(Talent):
    def __init__(self, rank):
        self.rank = rank

    @staticmethod
    def apply(stats: Stats):
        pass


class PaladinShieldSpecialization(Talent):
    def __init__(self, rank):
        self.rank = rank

    @staticmethod
    def apply(stats: Stats):
        pass


class WarriorShieldSpecialization(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.block += self.rank


class Anticipation(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.defense += self.rank * 4


class Defiance(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.expertise += 2 * self.rank


class ShieldMastery(Talent):
    def __init__(self, rank):
        self.rank = rank

    @staticmethod
    def apply(stats: Stats):
        pass


class Vitality(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.stamina *= (1 + .01 * self.rank)
        stats.strength *= (1 + .02 * self.rank)


class Toughness(Talent):
    def __init__(self, rank):
        self.rank = rank

    def apply(self, stats: Stats):
        stats.armor *= (1 + .02 * self.rank)
