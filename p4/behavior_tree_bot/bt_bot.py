#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn

# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')
 
    offensive_plan = Sequence(name='Offensive Strategy')
    attack_check = Check(close_takeable_planet)
    attack_action = Action(attack)
    offensive_plan.child_nodes = [attack_check, attack_action]

    spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_action = Action(spread)
    spread_sequence.child_nodes = [neutral_planet_check, spread_action]

    counter_sequence = Sequence(name='Counter Strategy')
    opponent_fleet_check = Check(fleet_to_counter)
    counter_action = Action(counter_enemy)
    follow_up_action = Sequence(name ='Reinforce Counter')
    follow_up_action.child_nodes = [offensive_plan.copy(), spread_sequence.copy()]
    counter_sequence.child_nodes = [opponent_fleet_check, counter_action, follow_up_action]

    root.child_nodes = [counter_sequence, offensive_plan, spread_sequence, attack_action.copy()]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        turn = 0
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
                turn += 1
                logging.info('turn: ' + str(turn))
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
