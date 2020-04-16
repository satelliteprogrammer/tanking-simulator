from utils import Stats


class Buff:
    @staticmethod
    def apply(stats: Stats):
        pass


class BoK(Buff):
    @staticmethod
    def apply(stats: Stats):
        pass

    @staticmethod
    def after(stats: Stats):
        stats.stamina *= 1.1
        stats.agility *= 1.1
        stats.strength *= 1.1


class iFortitude(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.stamina += 102


class iMotW(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.stamina += 18.9
        stats.agility += 18.9
        stats.strength += 18.9
        stats.armor += 459


class iCommandingShout(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.hp += 1350


class DevotionAura(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.armor += 861


class FlaskOfFortification(Buff):
    @staticmethod
    def apply(stats: Stats):
        def_def_ratio = 2.3654
        stats.defense += 10/def_def_ratio
        stats.hp += 1350


class ElixirOfMajorAgility(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.agility += 35


class ElixirOfMajorDefense(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.armor += 550


class StaminaFood(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.stamina += 30


class AgilityFood(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.agility += 20


class ScrollOfProtection(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.armor += 300


class SunwellRadiance(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.dodge -= 20
        stats.miss -= 5


class ScorpidSting(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.miss += 5


class InsectSwarm(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.miss += 2


class DualWielding(Buff):
    @staticmethod
    def apply(stats: Stats):
        stats.miss += 20