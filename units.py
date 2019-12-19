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

    def __init__(self, class_, defense, dodge, parry, block, block_value, stamina, buffs = ()):
        self.class_ = class_
        self.defense = defense
        self.dodge = dodge
        self.parry = parry
        self.block = block
        self.block_value = block_value
        self.stamina = stamina
        self.buffs = buffs


class Healer:
    ping = 0.1

    def __init__(self, class_, bh, haste, crit):
        self.class_ = class_
        self.bh = bh
        self.haste = haste
        self.crit = crit

    def decision(self, hp, timer):
        heal