from collections import deque
from utils import FightOver
import buffs as b
import encounter
import matplotlib.pyplot as plt
import multiprocessing as mp
import statistics as stat
import talents as t
import time
import units


def run(fight: encounter.Fight):
    fight.initialize()
    while True:
        try:
            fight.next()
        except FightOver:
            return fight.finish()


# results = list()
# def append_result(r):
#     results.append(r)


if __name__ == '__main__':

    '''
    Tank: sta, agi, str, def, ddg, par, blo, b_v, armor, hit, exp, spd, talents, buffs
    '''
    tank1 = units.PaladinTank(1200,  12,   0, 324, 221,  64, 100, 300, 15000,   0,   0, 1.6,
                              (t.CombatExpertise(5), t.SacredDuty(2), t.Deflection(5), t.RighteousFury(3),
                               t.PaladinShieldSpecialization(3), t.Anticipation(5), t.Toughness(5)),
                              (b.Fortitude, b.MotW, b.BoK))
    print(tank1)

    '''
    Boss: boss, level, dmg min - max, spd, school, abilities [11521, 22721]
    '''
    boss1 = units.Boss('Brutallus', 73, [8000, 16000], 2.0, 'physical')

    '''
    Boss: boss, level, dmg min - max, spd, school, abilities [11521, 22721]
    '''
    boss2 = units.Boss('Fathom-Guard Tidalvess', 73, [11099, 13992], 2.0, 'physical')

    '''
    Healer:                     bh,   haste, crit
    '''
    heal1 = units.PaladinHealer(2000, 100, 200)

    R = 1000
    r = 0

    start = time.time()

    # results = list()
    # while r < R:
    #     events = deque()
    #     result = run(encounter.Fight(boss1, tank1, heal1, 480, events))
    #     # print(result)
    #     results.append(result)
    #
    #     r += 1

    # pool = mp.Pool(mp.cpu_count())
    # for i in range(R):
    #     pool.apply_async(run, args=(boss1, tank1, heal1, 480), callback=append_result)
    # pool.close()
    # pool.join()

    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(run, [encounter.Fight(boss2, tank1, heal1, 480, deque()) for i in range(R)])

    print('Elapsed time {}s'.format(time.time() - start))

    deaths = []
    missed, dodged, parried, blocked, crushed, hit, totals, critical_events = ([] for i in range(8))
    for i, r in enumerate(results):
        if r[1] < 480:
            # print('Fight lasted {}s'.format(r[7]))
            # deaths.append(i)
            continue

        misses, dodges, parries, blocks, crushes, hits = r[0].get_stats()
        total = misses + dodges + parries + blocks + crushes + hits
        totals.append(total)
        missed.append(misses/total*100)
        dodged.append(dodges/total*100)
        parried.append(parries/total*100)
        blocked.append(blocks/total*100)
        crushed.append(crushes/total*100)
        hit.append(hits/total*100)
        critical_events.append(r[0].get_critical_events())

    print('missed mean: {} variance: {}'.format(stat.mean(missed), stat.stdev(missed)))
    print('dodged mean: {} variance: {}'.format(stat.mean(dodged), stat.stdev(dodged)))
    print('parried mean: {} variance: {}'.format(stat.mean(parried), stat.stdev(parried)))
    print('blocked mean: {} variance: {}'.format(stat.mean(blocked), stat.stdev(blocked)))
    print('crushed mean: {} variance: {}'.format(stat.mean(crushed), stat.stdev(crushed)))
    print('hit mean: {} variance: {}'.format(stat.mean(hit), stat.stdev(hit)))
    print('critical_events mean: {} variance: {}'.format(stat.mean(critical_events), stat.stdev(critical_events)))

    counter = 0

    for r in results:
        for t, hp in r[0].get_tank_hp().get_fight():
            if hp == 0:
                counter += 1

    print('Survived {} out of {}!'.format(R - counter, R))

    # if deaths:
    #     time = [hp[0] for hp in results[deaths[0]][8].hp]
    #     hp = [hp[1] for hp in results[deaths[0]][8].hp]
    #     plt.plot(time, hp)
    #     plt.show()