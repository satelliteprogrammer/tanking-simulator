class Heal:

    def __init__(self, name):
        self.name = name


class Ability:

    def __init__(self, name, damage, atk_speed, school):
        self.name = name
        self.damage = damage
        self.atk_speed = atk_speed
        self.school = school

        self.atk_timer = atk_speed


meteor_slash = Ability('Meteor Slash', 20000/9, 15, 'fire')