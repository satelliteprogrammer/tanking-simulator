from __future__ import annotations
from healers import PaladinHealer, DruidHealer
from mechanics import Fight
import buffs as b
import matplotlib.pyplot as plt
import multiprocessing as mp
import statistics as stat
import talents as ta
import time
import units


def run(fight: Fight):
    fight.initialize()
    fight.run()
    return fight.statistics()


# results = list()
# def append_result(r):
#     results.append(r)


def main():
    '''
    Tank: sta, agi, str, def, ddg, par, blo, b_v, armor, hit, exp, spd, talents, buffs
    '''
    pumpkinpie = units.PaladinTank(stamina=1345, agility=133, strength=0, defense_rating=418, dodge_rating=331,
                                   parry_rating=30, block_rating=62, block_value=318, armor=30400, hit_rating=48,
                                   expertise_rating=0, weapon_speed=1.8,
                                   talents=(ta.CombatExpertise(5), ta.SacredDuty(2), ta.Deflection(5),
                                            ta.RighteousFury(3), ta.PaladinShieldSpecialization(3),
                                            ta.Anticipation(5), ta.Toughness(5)),
                                   buffs=(b.iFortitude, b.iMotW, b.BoK, b.iCommandingShout, b.DevotionAura,
                                          b.FlaskOfFortification, b.StaminaFood, b.ScrollOfProtection,
                                          b.SunwellRadiance, b.InsectSwarm))
    print(pumpkinpie)

    '''
    Boss: boss, level, dmg min - max, spd, school, abilities [11521, 22721]
    '''
    kalecgos = units.Boss('Kalecgos', 73, [24000, 26000], 2.0, 'physical')

    '''
    Boss: boss, level, dmg min - max, spd, school, abilities [11521, 22721]
    '''
    boss2 = units.Boss('Fathom-Guard Tidalvess', 73, [11099, 13992], 1.5, 'physical')

    '''
    Healer:                     bh,   haste, crit
    '''
    eydel = PaladinHealer('Eydel', 2500, 0, 400)
    epiphron = DruidHealer('Epiphron', 2200, 191, 242)
    mawka = DruidHealer('Mawka', 2200, 191, 242)

    R = 10000
    r = 0

    start = time.time()

    # results = list()
    # while r < R:
    #     f = Fight(units.Boss('Sathrovarr', 73, [24000, 26000], 2, 'physical'),
    #               pumpkinpie,
    #               [PaladinHealer('Eydel', 2500, 0, 400),
    #                DruidHealer('Epiphron', 2200, 191, 242)],
    #               duration=480)
    #     result = run(f)
    #     # print(result)
    #     results.append(result)

    #     r += 1

    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(run, [Fight(units.Boss('Sathrovarr', 73, [24000, 26000], 2.0, 'physical'),
                                       pumpkinpie,
                                       [PaladinHealer('Eydel', 2500, 0, 400),
                                        DruidHealer('Epiphron', 2200, 191, 242)],
                                       duration=480) for i in range(R)])

    print('Elapsed time {}s'.format(time.time() - start))

    deaths = []
    missed, dodged, parried, blocked, crushed, hit, totals, critical_events = ([] for i in range(8))
    for i, result in enumerate(results):
        if result[0].get_tank_hp().get_hp() <= 0:
            deaths.append(i)
        misses, dodges, parries, blocks, crushes, hits = result[0].get_stats()
        total = misses + dodges + parries + blocks + crushes + hits
        totals.append(total)
        missed.append(misses/total*100)
        dodged.append(dodges/total*100)
        parried.append(parries/total*100)
        blocked.append(blocks/total*100)
        crushed.append(crushes/total*100)
        hit.append(hits/total*100)
        critical_events.append(result[0].get_critical_events())

    print('missed mean: {} variance: {}'.format(stat.mean(missed), stat.stdev(missed)))
    print('dodged mean: {} variance: {}'.format(stat.mean(dodged), stat.stdev(dodged)))
    print('parried mean: {} variance: {}'.format(stat.mean(parried), stat.stdev(parried)))
    print('blocked mean: {} variance: {}'.format(stat.mean(blocked), stat.stdev(blocked)))
    print('crushed mean: {} variance: {}'.format(stat.mean(crushed), stat.stdev(crushed)))
    print('hit mean: {} variance: {}'.format(stat.mean(hit), stat.stdev(hit)))
    print('critical_events mean: {} variance: {}'.format(stat.mean(critical_events), stat.stdev(critical_events)))

    print('{:.2f}% survival chance (survived {} out of {} tries)!'.format((R - len(deaths))/R * 100, R - len(deaths), R))

    # t = [hp[0] for hp in results[0][0].get_tank_hp().get_fight()]
    # hp = [hp[1] for hp in results[0][0].get_tank_hp().get_fight()]
    # plt.plot(t, hp)
    # plt.show()

    with open('history.log', 'w') as f:
        if not deaths:
            for line in results[0][1]:
                f.write(repr(line) + '\n')
            graph(results[0][0].get_tank_hp())
            print('First simulation written to history.log')
        else:
            for death in deaths:
                try:
                    death_recount = results[death][1][-40:]
                except IndexError:
                    death_recount = results[death][1]
                for line in death_recount:
                    f.write(repr(line) + '\n')
            print('All death recounts written to history.log')

    # if deaths:
    #     time = [hp[0] for hp in results[deaths[0]][8].hp]
    #     hp = [hp[1] for hp in results[deaths[0]][8].hp]
    #     plt.plot(time, hp)
    #     plt.show()
    # hist = results[0][0].get_tank_hp()
    # t = [p[0] for p in hist._hp]
    # hp = [p[1] for p in hist._hp]
    # plt.plot(t, hp)
    # plt.show()


def graph(tank_hp):
    fight = tank_hp.get_fight()
    time = [f[0] for f in fight]
    hp = [f[1] for f in fight]
    plt.plot(time, hp)
    plt.show()

if __name__ == '__main__':
    main()
