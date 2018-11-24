
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.
#hello charlie

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    best_node = None
    best_node = check_leafs(node, best_node)
    return best_node
    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    action = node.untried_actions.pop(0)
    new_state = board.next_state(state,action)
    new_child = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(new_state))
    node.child_nodes[action] = new_child
    return new_child
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    score = {}
    moves = []
    moves = board.legal_actions(state)
    temp_state = state
    while(board.is_ended(temp_state) == False):
        temp_state = board.next_state(temp_state, choice(moves))
        moves = moves.clear()
        moves = board.legal_actions(temp_state)
        score = board.points_values(temp_state)
    return score
        

    pass


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while(node.parent != None):
        node.visits += 1
        if(won == True):
            node.wins += 1
        node = node.parent
    node.visits += 1
    if(won == True):
        node.wins += 1
    pass


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node
        new_node = traverse_nodes(node, board, sampled_game, identity_of_bot)
        if new_node == None:
            break
        leaf = expand_leaf(new_node, board, sampled_game)
        score = rollout(board, sampled_game)

        won = False
        if ((identity_of_bot == 1 and score is {1: 1, 2: -1}) or identity_of_bot == 2 and score is {1: -1, 2: 1}):
            won = True

        backpropagate(leaf, won)

        # Do MCTS - This is all you!

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate
    selected = None
    for key, child in root_node.child_nodes.items():
        if(selected == None):
            selected = child
        else:
            if selected.visits < child.visits:
                selected = child
    return selected.parent_action

def evaluate_node(node):

    """
    This function evaluates a node following the formula seen in class
    """
    evaluation = 0
    if(node.visits != 0):
        evaluation = (node.wins / node.visits) + explore_faction * sqrt(log(node.parent.visits) / node.visits)
    return evaluation
def check_leafs(node, best_node):
    """
    This function goes through all the leafs reacheable from a given node and returns the best one according to evaluate node.
    A leaf is a node with untried actions left.
    """
    if(node.untried_actions):
        if(best_node == None):
            best_node = node
        if node.parent != None:
            if(evaluate_node(best_node) < evaluate_node(node)):
                best_node = node
    
    else:
        if node.child_nodes:
            for key, child in node.child_nodes.items():
                best_node = check_leafs(child, best_node)
    return best_node
