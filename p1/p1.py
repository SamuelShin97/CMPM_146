"""
p1.py
Samuel Shin, sayshin, 1510580
Partner: Sandra Latt, slatt
"""
from p1_support import load_level, show_level, save_level_costs
from math import inf, sqrt
from heapq import heappop, heappush, heapify

outfile = open("test_maze_path.txt", "w")

def dijkstras_shortest_path(initial_position, destination, graph, adj):
    """ Searches for a minimal cost path through a graph using Dijkstra's algorithm.

    Args:
        initial_position: The initial cell from which the path extends.
        destination: The end location for the path.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        If a path exits, return a list containing all cells from initial_position to destination.
        Otherwise, return None.

    """
    #pass
    queue = []
    dist = {}
    prev = {}

    heappush(queue, (0, initial_position)) #push the starting position into the queue
    dist[initial_position] = 0
    while(queue):
        current_cost, current_node = heappop(queue) 
        if current_node == destination:
            n = destination
            path = [n]
            while n is not initial_position:
                path.append(prev[n])
                n = prev[n]
            return path
        else:
            neighbors = adj(graph, current_node)
            for node, cost in neighbors: #node is the x,y coordinates for the neighbor we are looking at and cost is the cost of the edge joining the two points
                pathcost = cost + current_cost
                if node not in dist or pathcost < dist[node]:
                    dist[node] = pathcost
                    heappush(queue, (pathcost, node))
                    prev[node] = current_node
                
    return None             

def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """
    queue = []
    dist = {}
    prev = {}

    heappush(queue, (0, initial_position)) #push the starting position into the queue
    dist[initial_position] = 0
    while len(queue) > 0:
        current_cost, current_node = heappop(queue)
        for node, cost in adj(graph, current_node): #node is the x,y coordinates for the neighbor we are looking at and cost is the cost of the edge joining the two points
            pathcost = cost + current_cost
            if node not in dist or pathcost < dist[node]:
                dist[node] = pathcost
                heappush(queue, (pathcost, node))
                prev[node] = current_node
    return dist
    


def navigation_edges(level, cell):
    """ Provides a list of adjacent cells and their respective costs from the given cell.

    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        cell: A target location.

    Returns:
        A list of tuples containing an adjacent cell's coordinates and the cost of the edge joining it and the
        originating cell.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """
    neighbors = []

    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            n = (cell[0] + i, cell[1] + j)
            if n == cell:
                continue
            if n in level['spaces']:
                if abs(cell[0] - n[0]) == 1 and abs(cell[1] - n[1]) == 1:
                    dist = (0.5 * sqrt(2) * level['spaces'][cell]) + (0.5 * sqrt(2) * level['spaces'][n])
                else:
                    dist = (0.5 * level['spaces'][cell]) + (0.5 * level['spaces'][n])
                neighbors.append((n, dist))

    return neighbors

def test_route(filename, src_waypoint, dst_waypoint):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """

    # Load and display the level.
    level = load_level(filename)
    outfile.write(show_level(level) + '\n')

    # Retrieve the source and destination coordinates from the level.
    src = level['waypoints'][src_waypoint]
    dst = level['waypoints'][dst_waypoint]

    # Search for and display the path from src to dst.
    path = dijkstras_shortest_path(src, dst, level, navigation_edges)
    #print(path)
    if path:
        outfile.write(show_level(level, path) + '\n')
    else:
        print("No path possible!")
    
    

def cost_to_all_cells(filename, src_waypoint, output_filename):
    """ Loads a level, calculates the cost to all reachable cells from 
    src_waypoint, then saves the result in a csv file with name output_filename.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        output_filename: The filename for the output csv file.

    """
    
    # Load and display the level.
    level = load_level(filename)
    outfile.write(show_level(level) + '\n')

    # Retrieve the source coordinates from the level.
    src = level['waypoints'][src_waypoint]
    
    # Calculate the cost to all reachable cells from src and save to a csv file.
    costs_to_all_cells = dijkstras_shortest_path_to_all(src, level, navigation_edges)
    save_level_costs(level, costs_to_all_cells, output_filename)
    outfile.write('Saved file: ' + output_filename)


if __name__ == '__main__':
    filename, src_waypoint, dst_waypoint = 'my_maze.txt', 'a','e'

    # Use this function call to find the route between two waypoints.
    #test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_maze_costs.csv')
    navigation_edges(load_level(filename), (3, 1))
