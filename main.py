from collections import deque
import buffs as b
import encounter
import talents as t
import units

def run(fight : encounter.Fight):

    R = 1000
    r = 0

    while r < R:
        events = deque()
        fight.initialize(events)
        while len(events) > 0:
            do(t)

        r += 1


'''
Tank:                     sta, agi, str, def, ddg, par, blo, b_v, armor, hit, exp, spd, 
                           talents, buffs
'''
tank1 = units.PaladinTank(815,  12,   0, 324, 221,  64,   0, 300, 15000,   0,   0, 1.6,
                          (t.CombatExpertise(5), t.SacredDuty(2), t.Deflection(5), t.RighteousFury(3),
                           t.PaladinShieldSpecialization(3), t.Anticipation(5), t.Toughness(5)),
                          (b.Fortitude, b.MotW, b.BoK))

'''
Boss:              boss,        dmg min - max,  spd, school, abilities
'''
boss1 = units.Boss('Brutallus', [11521, 22721], 1.0, 'physical')

'''
Healer:                     bh,   haste, crit
'''
heal1 = units.PaladinHealer(1400, 0,     200)


fight = encounter.Fight(boss1, tank1, heal1, 480)

run(fight)
