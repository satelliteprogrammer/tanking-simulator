from math import floor
from random import uniform
from utils import Stats
import talents


class Boss:

    def __init__(self, name, damage, speed, school, abilities=None):
        self.name = name
        self.damage = damage
        self.speed = speed
        self.school = school
        self.abilities = abilities

    def attack(self):
        return self.damage

    def ability(self, name):
        if self.abilities is not None:
            return self.abilities[name].apply()
        else:
            return 0


class Tank:
    """
    https://wowwiki.fandom.com/wiki/Attribute?oldid=1598154
    https://wowwiki.fandom.com/wiki/Miss?oldid=1433070
    https://wowwiki.fandom.com/wiki/Dodge?oldid=1432727
    https://wowwiki.fandom.com/wiki/Parry?direction=next&oldid=1635714
    https://wowwiki.fandom.com/wiki/Block?oldid=1537907
    https://wowwiki.fandom.com/wiki/Defense?oldid=1619334
    https://wowwiki.fandom.com/wiki/Armor?oldid=1646912
    https://wowwiki.fandom.com/wiki/Combat_rating_system?oldid=1597988
    """
    base_defense = 370
    base_miss = 0
    base_dodge = 0
    base_parry = 5
    base_block = 5
    base_block_value = 0
    talent_parry = 5
    talent_block = 5
    talent_defense = 0
    agi_dodge_ratio = 0
    dodge_dodge_ratio = 18.9231
    parry_parry_ratio = 23.6538461538462
    block_block_ratio = 7.8846153846
    def_def_ratio = 2.36
    base_dr = 0

    def __init__(self, stamina: int, agility: int, strength: int, defense_rating: int, dodge_rating: int,
                 parry_rating: int, block_rating: int, block_value: int, armor: int, hit: int, expertise: int,
                 speed: float, talents: tuple = (), buffs: tuple = ()):

        self.stats = Stats(stamina, agility, strength, self.base_defense, self.base_miss, self.base_dodge,
                           self.base_parry, self.base_block, self.base_block_value, armor, hit, expertise)

        self.buffs = buffs
        for buff in buffs:
            buff.apply(self.stats)

        self.talents = talents
        for talent in talents:
            talent.apply(self.stats)

        for buff in buffs:
            if isinstance(buff, b.BoK):
                b.BoK.after(self.stats)

        self.stats.defense += defense_rating / self.def_def_ratio
        self.stats.miss += (self.stats.defense - 73 * 5) * .04
        self.stats.dodge += self.stats.agility / self.agi_dodge_ratio + dodge_rating / self.dodge_dodge_ratio + \
                            Tank.__defense_contribution(self.stats.defense, 73)
        self.stats.parry += parry_rating / self.parry_parry_ratio + Tank.__defense_contribution(self.stats.defense, 73)
        self.stats.block += block_rating / self.block_block_ratio + Tank.__defense_contribution(self.stats.defense, 73)
        self.stats.block_value += block_value

        self.speed = speed

    def get_hp(self):
        return floor(min(self.stats.stamina, 20) + (self.stats.stamina - min(self.stats.stamina, 20)) * 10)

    @staticmethod
    def __defense_contribution(defense: float, level: int) -> float:
        return (floor(defense) - level * 5) * 0.04

    def get_armor_reduction(self, level: int) -> float:
        """attacker 60+: DR% = Armor / (Armor + 400 + 85 * (AttackerLevel + 4.5 * (AttackerLevel - 59)))"""
        return (self.stats.armor / (self.stats.armor + 467.5 * level - 22167.5))/100

    def get_block_reduction(self) -> int:
        pass

    def attack(self):
        return self.speed


class PaladinTank(Tank):
    base_dodge = .65
    agi_dodge_ratio = 25

    def get_block_reduction(self) -> int:
        br = self.stats.block_value + self.stats.strength / 20
        for talent in self.talents:
            if isinstance(talent, t.PaladinShieldSpecialization):
                return floor(br * (1 + .1 * talent.rank))

        return floor(br)


class WarriorTank(Tank):
    base_dodge = .75
    agi_dodge_ratio = 30

    def get_block_reduction(self) -> int:
        br = self.stats.block_value + self.stats.strength / 20
        for talent in self.talents:
            if isinstance(talent, talents.ShieldMastery):
                return floor(br * (1 + .1 * talent.rank))

        return floor(br)


class Healer:
    haste_rating = 15.77
    crit_rating = 22.0769

    def __init__(self, bh, haste, crit):
        self.bh = bh
        self.haste = haste
        self.crit = crit

    def heal(self, hp, max_hp):
        pass


class PaladinHealer(Healer):
    # missing crit and libram calculations

    hl_eff = .714
    fol_eff = .429
    hl_inc = .12
    fol_inc = .17
    hl_inc_crit = .11
    fol_inc_crit = .5

    def heal(self, hp, max_hp):
        if hp < .9 * max_hp:
            return self.HL9()
        else:
            return self.FoL()

    def FoL(self):
        base = (458, 513)
        cast = 1.5 / (1 + (self.haste / self.haste_rating) / 100)
        heal = (uniform(base[0], base[1]) + self.bh * self.fol_eff) * (1 + self.fol_inc)

        return heal, cast

    def HL9(self):
        base = (1619, 1799)
        cast = 2 / (1 + (self.haste / self.haste_rating) / 100)
        heal = (uniform(base[0], base[1]) + self.bh * self.hl_eff) * (1 + self.hl_inc)

        return heal, cast
