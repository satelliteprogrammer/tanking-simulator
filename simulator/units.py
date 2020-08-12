from attr import attrs, attrib
from math import floor
from random import uniform

from .utils import Attributes, TankHP
import data.buffs as b
import data.talents as t


class Boss:

    def __init__(self, name, level, damage, weapon_speed, school, abilities=None):
        self.name = name
        self.level = level
        self.damage = damage
        self.weapon_speed = weapon_speed
        self.school = school
        self.abilities = abilities

    def attack(self):
        return floor(uniform(self.damage[0], self.damage[1]))

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
    base_defense = 350
    base_miss = 5
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
    def_def_ratio = 2.3654
    base_dr = 0
    base_hp = 0  # TODO

    hit_ratio = 15.7692
    expertise_ratio = 3.9423

    def __init__(self, stamina: int, agility: int, strength: int, defense_rating: int, dodge_rating: int,
                 parry_rating: int, block_rating: int, block_value: int, armor: int, hit_rating: int,
                 expertise_rating: int, weapon_speed: float, talents: tuple = (), buffs: tuple = ()):

        self.attributes = Attributes(stamina, agility, strength, self.base_defense, self.base_miss, self.base_dodge,
                                     self.base_parry, self.base_block, self.base_block_value, armor,
                                     hit_rating / self.hit_ratio, floor(expertise_rating / self.expertise_ratio),
                                     self.base_hp)

        self.buffs = buffs
        for buff in buffs:
            buff.apply(self.attributes)

        self.talents = talents
        for talent in talents:
            talent.apply(self.attributes)

        for buff in buffs:
            if isinstance(buff, b.BoK):
                b.BoK.after(self.attributes)

        self.attributes.defense += defense_rating / self.def_def_ratio
        self.attributes.miss += (self.attributes.defense - 73 * 5) * .04
        self.attributes.dodge += self.attributes.agility / self.agi_dodge_ratio + dodge_rating / self.dodge_dodge_ratio + \
                                 Tank.__defense_contribution(self.attributes.defense, 73)
        self.attributes.parry += parry_rating / self.parry_parry_ratio + Tank.__defense_contribution(
            self.attributes.defense, 73)
        self.attributes.block += block_rating / self.block_block_ratio + Tank.__defense_contribution(
            self.attributes.defense, 73)
        self.attributes.block_value += block_value

        self.weapon_speed = weapon_speed

        self.attributes.hp += min(self.attributes.stamina, 20) + (
                    self.attributes.stamina - min(self.attributes.stamina, 20)) * 10
        self.attributes.hp = floor(self.attributes.hp)

    @staticmethod
    def __defense_contribution(defense: float, level: int) -> float:
        return (floor(defense) - level * 5) * 0.04

    def get_armor_reduction(self, level: int) -> float:
        """attacker 60+: DR = Armor / (Armor + 400 + 85 * (AttackerLevel + 4.5 * (AttackerLevel - 59)))"""
        return min(.75, self.attributes.armor / (self.attributes.armor + 467.5 * level - 22167.5))

    def get_block_reduction(self) -> int:
        pass

    def attack(self):
        return self.weapon_speed

    def __repr__(self):
        stats = self.attributes
        str = 'Tank\nstamina: {:.0f}, agility: {:.0f}, strength: {:.0f}, armor: {:.0f}, defense: {:.0f},\n' \
              'miss: {:.2f}%, dodge: {:.2f}%, parry: {:.2f}%, block: {:.2f}%\n' \
              'hp = {}\nhard avoidance = {:.2f}%\ndamage mitigation = {:.2f}%' \
              ''.format(stats.stamina, stats.agility, stats.strength, stats.armor, stats.defense,
                        stats.miss, stats.dodge, stats.parry, stats.block, stats.hp,
                        stats.miss + stats.dodge + stats.parry, self.get_armor_reduction(73) * 100)
        return str


class PaladinTank(Tank):
    base_dodge = .65
    agi_dodge_ratio = 25

    def __init__(self, stamina: int, agility: int, strength: int, defense_rating: int, dodge_rating: int,
                 parry_rating: int, block_rating: int, block_value: int, armor: int, hit_rating: int,
                 expertise_rating: int, weapon_speed: float, talents: tuple = (), buffs: tuple = ()):

        super().__init__(stamina, agility, strength, defense_rating, dodge_rating, parry_rating, block_rating,
                         block_value, armor, hit_rating, expertise_rating, weapon_speed, talents, buffs)

        self.attributes.block += 30

    def get_block_reduction(self) -> int:
        br = self.attributes.block_value + self.attributes.strength / 20
        for talent in self.talents:
            if isinstance(talent, t.PaladinShieldSpecialization):
                return floor(br * (1 + .1 * talent.rank))

        return floor(br)


class WarriorTank(Tank):
    base_dodge = .75
    agi_dodge_ratio = 30

    def __init__(self, stamina: int, agility: int, strength: int, defense_rating: int, dodge_rating: int,
                 parry_rating: int, block_rating: int, block_value: int, armor: int, hit_rating: int,
                 expertise_rating: int, weapon_speed: float, talents: tuple = (), buffs: tuple = ()):

        super().__init__(stamina, agility, strength, defense_rating, dodge_rating, parry_rating, block_rating,
                         block_value, armor, hit_rating, expertise_rating, weapon_speed, talents, buffs)

        self.attributes.block += 75

    def get_block_reduction(self) -> int:
        br = self.attributes.block_value + self.attributes.strength / 20
        for talent in self.talents:
            if isinstance(talent, t.ShieldMastery):
                return floor(br * (1 + .1 * talent.rank))

        return floor(br)


@attrs(slots=True, repr=False, eq=False)
class Healer:
    _haste_ratio = attrib(init=False, default=15.77)
    _crit_ratio = attrib(init=False, default=22.0769)

    name = attrib(type=str)
    bonus_healing = attrib(type=int)
    haste_rating = attrib(type=int)
    crit_rating = attrib(type=int)
    latency = attrib(default=0, type=float)
    haste = attrib(init=False, default=0)
    crit = attrib(init=False, default=0)

    def __attrs_post_init__(self):
        self.haste = self.haste_rating / self._haste_ratio / 100
        self.crit = self.crit_rating / self._crit_ratio / 100

    def decision(self, time: float, tank: TankHP):
        raise NotImplementedError()

    def boost(self, bonus_healing: int = 0, haste: float = 0, haste_rating: int = 0, crit: float = 0,
              crit_rating: int = 0):

        if haste_rating:
            self.haste += haste_rating / self._haste_ratio / 100
        if crit_rating:
            self.crit += crit_rating / self._crit_ratio / 100
        self.bonus_healing += bonus_healing
        self.haste += haste
        self.crit += crit

    def gcd(self):
        return 1.5/(1 + self.haste)

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __repr__(self):
        return f'{self.name}\n' \
               f'Bonus Healing: {self.bonus_healing} Haste: {self.haste * 100}% Crit: {self.crit * 100}%'
