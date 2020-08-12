# Tanking Simulator

This is a tanking emulator designed for World of Warcraft The Burning Crusade.

### In development

This project is still in development.

## Instalation

The `requirements.txt` lists all python library dependencies required. They can be installed using:

```
pip install -r requirements.txt
```

## Usage

The simulation can be started by running

```
python main.py
```

## Setting up the simulation

The simulation parameters are the `Tank`, the available `Healer`s and the `Boss` being fought, aswell as the duration of the fight and number of simulations.
These are entered directly by modifiying the multiprocessing `map` method in `main.py`, as demonstrated below:

```python
R = 10000

tank = units.PaladinTank(stamina=1345, agility=133, strength=0, defense_rating=418, dodge_rating=331,
                         parry_rating=30, block_rating=62, block_value=318, armor=30400, hit_rating=48,
                         expertise_rating=0, weapon_speed=1.8,
                         talents=(ta.CombatExpertise(5), ta.SacredDuty(2), ta.Deflection(5),
                                  ta.RighteousFury(3), ta.PaladinShieldSpecialization(3),
                                  ta.Anticipation(5), ta.Toughness(5)),
                         buffs=(b.iFortitude, b.iMotW, b.BoK, b.iCommandingShout, b.DevotionAura,
                                b.FlaskOfFortification, b.StaminaFood, b.ScrollOfProtection,
                                b.SunwellRadiance, b.InsectSwarm))

with mp.Pool(mp.cpu_count()) as pool:
    results = pool.map(run, [Fight(units.Boss('Sathrovarr', level=73, damage=[24000, 26000], weapon_speed=2.0,
                                              school='physical', abilities=None),
                                   tank,
                                   [PaladinHealer('healer 1', bonus_healing=2500, haste_rating=0, crit_rating=400),
                                    DruidHealer('healer 2', bonus_healing=2200, haste_rating=191, crit_rating=242)],
                                   duration=480) for i in range(R)])
```

### Adding Healer strategies

Additional healing strategies and Heal classes can be added in `data/healers.py`. To illustrate, there is an additional class named `Eydel` derived from `PaladinHealer` that overrides the `decision` method with it's own tactics.

#### `decision` method

The decision method is called each time a healer is required to many a decision and takes as parameters the `time` of the fight and the `tankHP`, an object of a class which holds the tank health throughout the fight.

**Note:** In the future, this method should be refactored to receive instead the entire fight, as decisions can be taken with more information than the time of the fight and the tank HP.

### Adding Fights and Bosses

Additional boss fights are added by modifying the `Boss` parameters and adding abilities. New abilities can be added in `data/abilities.py` file and passed as a `List` when creating the boss.

**Warning:** Not fully implemented.

### Tank

The tank doesn't need to be created for each simulation run, and takes it's attributes as parameters. There are 2 tank classes created, Paladin and Warrior. Druid isn't implemented yet. Any additional buffs and talents can be added in `data/buffs.py` and `data/talents.py` respectively.

## License
[MIT](https://choosealicense.com/licenses/mit/)
