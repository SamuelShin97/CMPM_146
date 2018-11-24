import sys
sys.path.insert(0, '../')
from math import inf, ceil, floor
from planet_wars import issue_order
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

def counter_enemy(state):
    my_planets = state.my_planets()
    target_planets = [planet for planet in (state.not_my_planets() + state.my_planets())
                      if any(fleet.destination_planet == planet.ID for fleet in state.enemy_fleets())]
    def sum_fleets(state, planet):
        enemy_ships_attacking = 0
        avg_enemy_dist = 0
        num_enemy_attacking_fleets = 0
        for enemyFleet in state.enemy_fleets():
            if enemyFleet.destination_planet == planet.ID:
                enemy_ships_attacking += enemyFleet.num_ships
                num_enemy_attacking_fleets += 1
                avg_enemy_dist += enemyFleet.turns_remaining
        if num_enemy_attacking_fleets > 0:
            avg_enemy_dist = avg_enemy_dist / num_enemy_attacking_fleets
        logging.info("Ships heading to planet " + str(planet.ID) + " from enemy: " + str(enemy_ships_attacking) + " avg dist: " + str(avg_enemy_dist))
        my_ships_attacking = 0
        avg_my_dist = 0
        num_my_attacking_fleets = 0
        for myFleet in state.my_fleets():
            if myFleet.destination_planet == planet.ID:
                my_ships_attacking += myFleet.num_ships
                num_my_attacking_fleets += 1
                avg_my_dist += myFleet.turns_remaining
        if num_my_attacking_fleets > 0:
            avg_my_dist = avg_my_dist / num_my_attacking_fleets
        logging.info("Ships heading to planet " + str(planet.ID) + " from me: " + str(my_ships_attacking) + " avg dist: " + str(avg_my_dist))
        ships_on_planet = -planet.num_ships if planet in my_planets else planet.num_ships
        logging.info("Ships already on planet "  + str(planet.ID) + ": " + str(abs(ships_on_planet)) + " Planet is owned by me: " + str(planet in my_planets))
        return (enemy_ships_attacking - my_ships_attacking) + ships_on_planet, avg_enemy_dist, avg_my_dist

    def find_best_counter_planet(state, target, sum, avg_attacker_dist, avg_my_dist):
        best = None
        bestShips = 0
        bestDist = inf
        for my_planet in my_planets:
            dist = state.distance(my_planet.ID, target.ID)
            ships_generated = ((avg_my_dist if avg_my_dist > 0 else dist) - avg_attacker_dist) * target.growth_rate
            required_ships = ships_generated + 1 + sum 
            if required_ships < 1:
                return None, 0
            x, y, z = sum_fleets(state, my_planet)
            logging.info("sum_fleets_my_planet: " + str(x))
            logging.info("ships_generated: " + str(ships_generated))
            logging.info("required ships: " + str(required_ships) + " dist: " + str(dist) + " my ships (planet " + str(my_planet.ID) + "): " + str(my_planet.num_ships))
            if my_planet.ID != target.ID and -x + ((y) * my_planet.growth_rate) >= required_ships and dist < bestDist:
                best = my_planet
                bestDist = dist
                bestShips = required_ships
        return best, bestShips
    
    counters = 0
    for target in target_planets:
        sum_attacking, avg_attacker_dist, avg_my_dist = sum_fleets(state, target)
        ships_generated_init = avg_attacker_dist * target.growth_rate if target in state.my_planets() else 0
        logging.info("sum of planet " + str(target.ID) + ": " + str(sum_attacking))
        if sum_attacking + ships_generated_init < 1:
            continue
        planet, ships = find_best_counter_planet(state, target, sum_attacking, avg_attacker_dist, avg_my_dist)
        if planet != None:
            logging.info('COUNTERING NOW')
            issue_order(state, planet.ID, target.ID, ships)
            counters += 1
    logging.info("COUNTERS: " + str(counters))
    return counters >= 1

def attack(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    enemy_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)
    try:
        ret = False
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1
            if my_planet.num_ships > required_ships and state.distance(my_planet.ID, target_planet.ID) < 1000:
                ret = True
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)
    except StopIteration:
        return  ret
    pass

def spread(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)
    try:
        ret = False
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1
            if my_planet.num_ships > required_ships and required_ships < my_planet.num_ships/2:
                ret = True
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)                
            else:
                my_planet = next(my_planets)
    except StopIteration:
        return ret
    pass