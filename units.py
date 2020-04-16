from heals import Heal, HoT, LB, REG, Shield
from math import floor
from random import uniform
from utils import Stats, TankHP
import buffs as b
import talents as t


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

        self.attributes = Stats(stamina, agility, strength, self.base_defense, self.base_miss, self.base_dodge,
                                self.base_parry, self.base_block, self.base_block_value, armor,
                                hit_rating/self.hit_ratio, floor(expertise_rating/self.expertise_ratio), self.base_hp)

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

        self.attributes.hp += min(self.attributes.stamina, 20) + (self.attributes.stamina - min(self.attributes.stamina, 20)) * 10
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
        str = 'Paladin Tank\nstamina: {}, agility: {}, strength: {}, armor: {}\n' \
              'defense: {}, miss: {}%, dodge: {}%, parry: {}%, block: {}%\n' \
              'hp = {}\nhard avoidance = {}%\ndamage mitigation = {}%' \
              ''.format(stats.stamina, stats.agility, stats.strength, stats.armor, stats.defense, stats.miss,
                        stats.dodge, stats.parry, stats.block, stats.hp,
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


class Healer:
    haste_ratio = 15.77 * 100
    crit_ratio = 22.0769 * 100

    def __init__(self, name, bh, haste_rating, crit_rating, latency=0):
        self.name = name

        self.bh = bh
        self.haste = haste_rating / self.haste_ratio
        self.crit = crit_rating / self.crit_ratio

        self.casting = None
        self.gcd = 1.5 / (1 + self.haste)
        self.latency = latency

    def heal(self):
        if self.casting:
            heal = self.casting.apply()
            self.casting = None
            return heal
        else:
            return None

    def decision(self, tank: TankHP) -> Heal:
        pass

    def cast(self) -> Heal:
        spell = self.casting
        self.casting = None
        return spell

    def current_cast(self) -> Heal:
        return self.casting

    def __repr__(self):
        return f'{self.name} {self.bh}/{self.haste:.2f}/{self.crit:.2f} (bh/haste/crit) is casting {self.casting} ({id(self)})\n'


class PaladinHealer(Healer):
    hl_eff = .714
    fol_eff = .429
    hl_inc = 1.12
    fol_inc = 1.17
    hl_inc_crit = .11
    fol_inc_crit = .5

    def __init__(self, bh, haste_rating, crit_rating, latency=0):
        super().__init__(bh, haste_rating, crit_rating, latency)

        self.FoL = Heal('Flash of Light', (458, 513), 1.5, self.fol_eff, self.fol_inc, self.fol_inc_crit, self)
        self.HL9 = Heal('Holy Light (Rank 9)', (1619, 1799), 2, self.hl_eff, self.hl_inc, self.hl_inc_crit, self)

    def decision(self, tank: TankHP) -> Heal:
        if tank.get_hp() < .8 * tank.full:
            self.casting = self.HL9
        else:
            self.casting = self.FoL

        return self.casting


class DruidHealer(Healer):
    """
    rej, 1x life (before battle)
    light: rejuvenation, 3x lifeblooms, regrowth if low
    medium: always use regrowth or .65/7
    heavy: rej, 2x life, regrowth, use healing touch

    swiftmend: uses the hot with the least time to end

    LB: the LB ticks are kept with the same initial schedule
        the bloom will happen 7s after the last application
        the have the timer
    """

    ht_eff = 1.2
    lb_dh_eff = .3429 * 1.2
    lb_hot_eff = .5180 * 1.2
    rej_eff = .8 * 1.2
    reg_dh_eff = .3 * 1.2
    reg_hot_eff = .7 * 1.2
    swiftmend_rej_eff = 1
    tranq_eff = .73 * 1.2

    ht_inc = 1.1
    lb_inc = 1.1
    rej_inc = 1.1 * 1.15
    reg_inc = 1.1
    ht_inc_crit = .03
    lb_inc_crit = .03
    reg_inc_crit = .53

    MT_healing_init = ('REJ', 'LB', 'LB', 'LB', 'REG', None, None)
    MT_healing = (MT_healing_init, 'LB', 'REJ', 'REG', None, 'LB', None, None, None)
    OT_healing_init = ('REJ', None, 'LB', None, 'LB', None)
    OT_healing = (OT_healing_init, 'LB', 'REJ', None, None, 'LB', None, None, None)

    def __init__(self, bh, haste_rating, crit_rating, latency=0, strategy='MT_healing'):
        super().__init__(bh, haste_rating, crit_rating, latency)

        self.HT = Heal('Healing Touch', (2707, 3197), 3, self.ht_eff, self.ht_inc, self.ht_inc_crit, self)
        self.LB = LB('Lifebloom', 273, 0, self.lb_hot_eff, self.lb_inc, self, stack=3, duration=7, tick_period=1)
        self.LB_HEAL = Heal('Lifebloom blooms', (600, 600), 0, self.lb_dh_eff, self.lb_inc, self.lb_inc_crit, self)
        self.REG_HOT = HoT('Regrowth', 1274, 0, self.reg_hot_eff, self.reg_inc, self, stack=1, duration=21, tick_period=3)
        self.REG = REG('Regrowth', (1215, 1355), 2, self.reg_dh_eff, self.reg_inc, self.reg_inc_crit, self)
        self.REJ = HoT('Rejuvenation', 1060, 0, self.rej_eff, self.rej_inc, self, stack=1, duration=12, tick_period=3)

        self.empty = Heal('Global CD', (0, 0), 0, 0, 0, 0, self)

        if strategy == 'MT_healing':
            self.strategy = self.MT_healing
        elif strategy == 'OT_healing':
            self.strategy = self.OT_healing

        self.init = True
        self.counter = 0

    def decision(self, tank: TankHP) -> Heal:
        spell = None
        if self.init:
            try:
                spell = self.strategy[0][self.counter]
                self.counter += 1
            except IndexError:
                self.init = False
                self.counter = 1

        if not self.init:
            spell = self.strategy[self.counter]
            self.counter += 1
            if self.counter > 8:
                self.counter = 1

        if spell:
            casting = eval("self." + spell)
            if not isinstance(casting, HoT):
                self.casting = casting
            else:
                casting.reset()
        else:
            casting = self.empty

        return casting


class ShamanHealer(Healer):
    """
    Default strategy is getting 1st/2nd jumps of the chain heal. This takes into consideration that the rshaman
    must be healing the melees
    """

    hw_eff = .857 * 1.1
    lhw_eff = .428 * 1.1
    ch_eff = .714 * 1.1 * 1.2
    es_eff = .286

    hw_inc = 1.1
    lhw_inc = 1.1
    ch_inc = 1.1 * 1.2

    hw_inc_crit = .05
    lhw_inc_crit = .05
    ch_inc_crit = .05

    def __init__(self, name, bh, haste_rating, crit_rating):
        super().__init__(name, bh, haste_rating, crit_rating)

        self.HW = Heal('Healing Wave', (2134, 2437), 2.5, self.hw_eff, self.hw_inc, self.hw_inc_crit, self)
        self.LHW = Heal('Lesser Healing Wave', (1039, 1186), 1, self.lhw_eff, self.lhw_inc, self.lhw_inc_crit, self)
        self.CH5 = Heal('Chain Heal (Rank 5)', (826, 943), 2, self.ch_eff, self.ch_inc, self.ch_inc_crit, self)
        self.CH4 = Heal('Chain Heal (Rank 4)', (605, 692), 2, self.ch_eff, self.ch_inc, self.ch_inc_crit, self)
        self.ES = Shield('Earth Shield', 270, 0, self.es_eff, self)

    def decision(self, tank: TankHP) -> Heal:
        self.casting = self.CH4
        return self.casting
