

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def close_takeable_planet(state):
    for my_planet in state.my_planets():
        for target in state.enemy_planets():
            if state.distance(my_planet.ID, target.ID) < 1000 and my_planet.num_ships > target.num_ships:
                return True
    return False

def fleet_to_counter(state):
    return len(state.enemy_fleets()) >= 1
