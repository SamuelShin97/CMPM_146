import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import shutil
import time
import math

width = 200
height = 16

"""
options = [
    "-",  # an empty space
    "X",  # a solid wall
    "?",  # a question mark block with a coin
    "M",  # a question mark block with a mushroom
    "B",  # a breakable block
    "o",  # a coin
    "|",  # a pipe segment
    "T",  # a pipe top
    "E",  # an enemy
    #"f",  # a flag, do not generate
    #"v",  # a flagpole, do not generate
    #"m"  # mario's start position, do not generate
]
"""
#weight different possibilities 
options = ["-"] * 100 + ["X"] * 10 + ["?"] * 1 + ["M"] * 1 + ["o"] * 1 + ["|"] * 1 + ["T"] * 1 + ["E"] * 1

# The level as a grid of tiles


class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    # Update this individual's estimate of its fitness.
    # This can be expensive so we do it once and then cache the result.
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Print out the possible measurements or look at the implementation of metrics.py for other keys:
        # print(measurements.keys())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Modify this, and possibly add more metrics.  You can replace this with whatever code you like.
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.8,
            emptyPercentage=1.0,
            linearity=-0.5,
            solvability=2.0
        ) #tweeked slightly to get more open space
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients))
        return self

    # Return the cached fitness value or calculate it as needed.
    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    # Mutate a genome into a new genome.  Note that this is a _genome_, not an individual!
    def mutate(self, genome):
        # STUDENT implement a mutation operator, also consider not mutating this individual
        # STUDENT also consider weighting the different tile types so it's not uniformly random
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        
        mutation_chance = 0.1 #chance to mutate 10%(low)
        #add in multiples for weights
        level_middle_replacements = ["-", "-", "-", "-", "-", "-", "-", "X", "X", "?", "M", "B", "B", "o",  "o", "E"]
        #ground can only be a space or a floor
        level_bottom_replacements = ["-", "X"]
        
        #don't mess up sides
        left = 2
        right = width - 3
        
        
        for y in range(height):
            for x in range(left, right):
                #--- our mutations start here ---
                
                if random.random() < mutation_chance:
                    #if its the floor, only allow floor placements ("-" or "X")
                    if y == height - 1:
                        genome[y][x] = random.sample(level_bottom_replacements, 1)[0]
                    #if its the sky, leave blank
                    elif y < 6:
                        genome[y][x] = "-"
                    #if its in the middle, replace randomly with weighted list options
                    else:
                        genome[y][x] = level_middle_replacements[random.randint(0, len(level_middle_replacements)-1)]
                """
                #pipe must have floor under it
                if y < 15:
                    if genome[y][x] == "|" and (genome[y+1][x] != "X"):
                        genome[y][x] = "-"
                
                #Don't allow pipes to fly in the sky
                if y < height - 4 and (genome[y][x] == "T" or genome[y][x] == "|"):
                    genome[y][x] = "-"
                    
                #Don't allow pipes to hover over holes
                if genome[y][x] == "T" and genome[15][x] == "-":
                	genome[y][x] = "-"
                
                #Cap off pipes
                if genome[y][x] == "|" and (genome[y-1][x] != "T"):
                    genome[y-1][x] = "T"
                """
                #if its a top and is in a valid position
                if genome[y][x] == "T" and y >= 11:
                    #if there is another top or pipe directly next to it, delete it
                    if genome[y][x + 1] == "T" or genome[y][x + 1] == "|":
                        genome[y][x + 1] = "-"
                    #if the space below is not a pipe, set it to a pipe
                    if y + 1 < 16 and genome[y+1][x] != "|":
                        genome[y + 1][x] = "|"
                #if its a top but not in a valid position
                elif genome[y][x] == "T" and y < 11:
                    genome[y][x] = "-"
                #if its a pipe and in a valid position
                if genome[y][x] == "|" and y >= 12:
                    #if the above piece is not a top nor another pipe
                    if genome[y - 1][x] != "T" and genome[y - 1][x] != "|":
                        #cap the pipe with a top
                        genome[y - 1][x] = "T"
                    #if there is another top or pipe directly next to it, delete it 
                    if genome[y][x + 1] == "T" or genome[y][x + 1] == "|":
                        genome[y][x + 1] = "-"
                    #if the space below is valid and the space below is not another pipe or solid block
                    if y + 1 < 16 and genome[y + 1][x] != "|" and genome[y + 1][x] != "X":
                        #if at the ground floor, randomly choose to place a ground tile in or pipe all the way down
                        if y + 1 == 15:
                            arr = ["X", "|"]
                            choice = random.choice(arr)
                            genome[y + 1][x] = choice
                        #if not at the ground level yet, put in a pipe
                        else:
                            genome[y + 1][x] = "|"

                elif genome[y][x] == "|" and y < 12:
                    genome[y][x] = "-"

                #if theres a gap, make it big enough to jump into
                if y < height-1 and x < width-1 and genome[y][x] == "-" and genome[y+1][x] != "-" and genome[y-1][x] != "-":
                    genome[y-1][x] = "-"

        for col in range(height):
            genome[col][-1] = "-"

        for col in range(8, 14):
            genome[col][-2] = "f"
        for col in range(14, 16):
            genome[col][-2] = "X"
        genome[7][-2] = "v"
                
        return genome

    # Create zero or more children from self and other
    def generate_children(self, other):
    
        new_self_genome = copy.deepcopy(self.genome)
        new_other_genome = copy.deepcopy(other.genome)
        self_genome = copy.deepcopy(self.genome)
        other_genome = copy.deepcopy(other.genome)
        # Leaving first and last columns alone...
        # do crossover with other
        
        random_crossover = random.randint(2, width-2)
        left = 1
        right = width - 1
        
        for y in range(height):
            for x in range(left, right):
                #create two possibilities
                if x < random_crossover:
                    new_self_genome[y][x] = self_genome[y][x]
                    new_other_genome[y][x] = other_genome[y][x]
                else:
                    new_other_genome[y][x] = self_genome[y][x]
                    new_self_genome[y][x] = other_genome[y][x]
        
        #return the best of the two
        if self.fitness() > other.fitness():
            final_genome = self.mutate(new_self_genome)
        else:
            final_genome = self.mutate(new_other_genome)
            
            
        return (Individual_Grid(final_genome),)

        

    # Turn the genome into a level string (easy for this genome)
    def to_level(self):
        return self.genome

    # These both start with every floor tile filled with Xs
    # STUDENT Feel free to change these
    @classmethod
    def empty_individual(cls):
        g = [["-" for col in range(width)] for row in range(height)]
        g[15][:] = ["X"] * width
        g[14][0] = "m"
        g[7][-1] = "v"
        for col in range(8, 14):
            g[col][-1] = "f"
        for col in range(14, 16):
            g[col][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        # STUDENT consider putting more constraints on this to prevent pipes in the air, etc
        # STUDENT also consider weighting the different tile types so it's not uniformly random
       
        genome = [random.choices(options, k=width) for row in range(height)]
        
        left = 1
        right = width - 1
        
        for y in range(height):
            for x in range(left, right):
                
                #leave sky blank
                if y < 6:
                    genome[y][x] = "-"
                """
                #pipe must have floor under it
                if y < 15:
                    if genome[y][x] == "|" and (genome[y+1][x] != "X"):
                        genome[y][x] = "-"
                
                #Don't allow pipes to fly in the sky
                if y < height - 4 and (genome[y][x] == "T" or genome[y][x] == "|"):
                    genome[y][x] = "-"
                    
                #Don't allow pipes to hover over holes
                if genome[y][x] == "T" and genome[15][x] == "-":
                	genome[y][x] = "-"
                
                #Cap off pipes
                if genome[y][x] == "|" and (genome[y-1][x] != "T"):
                    genome[y-1][x] = "T"
                """
                
                #if theres a gap, make it big enough to jump into
                if y < height-1 and x < width-1 and genome[y][x] == "-" and genome[y+1][x] != "-" and genome[y-1][x] != "-":
                    genome[y-1][x] = "-"
                
                #sides stay blank
                if x == 1 or x > right-3:
                    genome[y][x] = "-"

        for col in range(height):
            genome[col][0] = "-"   

        genome[15][:] = ["X"] * width
        genome[14][0] = "m"
        genome[7][-2] = "v"
        #genome[8:14][-1] = ["f"] * 6
        #genome[14:16][-1] = ["X", "X"]
        for col in range(8, 14):
            genome[col][-2] = "f"
        for col in range(14, 16):
            genome[col][-2] = "X"
      
        return cls(genome)
       


def offset_by_upto(val, variance, min=None, max=None):
    val += random.normalvariate(0, variance**0.5)
    if min is not None and val < min:
        val = min
    if max is not None and val > max:
        val = max
    return int(val)


def clip(lo, val, hi):
    if val < lo:
        return lo
    if val > hi:
        return hi
    return val

# Inspired by https://www.researchgate.net/profile/Philippe_Pasquier/publication/220867545_Towards_a_Generic_Framework_for_Automated_Video_Game_Level_Creation/links/0912f510ac2bed57d1000000.pdf


class Individual_DE(object):
    # Calculating the level isn't cheap either so we cache it too.
    __slots__ = ["genome", "_fitness", "_level"]

    # Genome is a heapq of design elements sorted by X, then type, then other parameters
    def __init__(self, genome):
        self.genome = list(genome)
        heapq.heapify(self.genome)
        self._fitness = None
        self._level = None

    # Calculate and cache fitness
    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        # Default fitness function: Just some arbitrary combination of a few criteria.  Is it good?  Who knows?
        # STUDENT Add more metrics?
        # STUDENT Improve this with any code you like
        coefficients = dict(
            meaningfulJumpVariance=0.5,
            negativeSpace=0.6,
            pathPercentage=0.5,
            emptyPercentage=0.6,
            linearity=-0.5,
            solvability=2.0
        )
        penalties = 0
        # STUDENT For example, too many stairs are unaesthetic.  Let's penalize that
        if len(list(filter(lambda de: de[1] == "6_stairs", self.genome))) > 5:
            penalties -= 2
        if len(list(filter(lambda de: de[1] == "4_block", self.genome))) == 1:
            penalties -= 1
        if len(list(filter(lambda de: de[1] == "0_hole", self.genome))) == 1:
            penalties -= 1
        if len(list(filter(lambda de: de[1] == "3_coin", self.genome))) > 3:
            penalties += 1
        if len(list(filter(lambda de: de[1] == "2_enemy", self.genome))) > 3:
            penalties -= 1
        
        # STUDENT If you go for the FI-2POP extra credit, you can put constraint calculation in here too and cache it in a new entry in __slots__.
        self._fitness = sum(map(lambda m: coefficients[m] * measurements[m],
                                coefficients)) + penalties
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, new_genome):
        # STUDENT How does this work?  Explain it in your writeup.
        # STUDENT consider putting more constraints on this, to prevent generating weird things
        if random.random() < 0.5 and len(new_genome) > 0:
            to_change = random.randint(0, len(new_genome) - 1)
            de = new_genome[to_change]
            new_de = de
            x = de[0]
            de_type = de[1]
            choice = random.random()
            if de_type == "4_block":
                y = de[2]
                breakable = de[3]
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    breakable = not de[3]
                new_de = (x, de_type, y, breakable)
            elif de_type == "5_qblock":
                y = de[2]
                has_powerup = de[3]  # boolean
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                else:
                    has_powerup = not de[3]
                new_de = (x, de_type, y, has_powerup)
            elif de_type == "3_coin":
                y = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    y = offset_by_upto(y, height / 2, min=0, max=height - 1)
                new_de = (x, de_type, y)
            elif de_type == "7_pipe":
                h = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    h = offset_by_upto(h, 2, min=2, max=height - 4)
                new_de = (x, de_type, h)
            elif de_type == "0_hole":
                w = de[2]
                if choice < 0.5:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                else:
                    w = offset_by_upto(w, 4, min=1, max=width - 2)
                new_de = (x, de_type, w)
            elif de_type == "6_stairs":
                h = de[2]
                dx = de[3]  # -1 or 1
                if choice < 0.33:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.66:
                    h = offset_by_upto(h, 8, min=1, max=height - 4)
                else:
                    dx = -dx
                new_de = (x, de_type, h, dx)
            elif de_type == "1_platform":
                w = de[2]
                y = de[3]
                madeof = de[4]  # from "?", "X", "B"
                if choice < 0.25:
                    x = offset_by_upto(x, width / 8, min=1, max=width - 2)
                elif choice < 0.5:
                    w = offset_by_upto(w, 8, min=1, max=width - 2)
                elif choice < 0.75:
                    y = offset_by_upto(y, height, min=0, max=height - 1)
                else:
                    madeof = random.choice(["?", "X", "B"])
                new_de = (x, de_type, w, y, madeof)
            elif de_type == "2_enemy":
                pass
            new_genome.pop(to_change)
            heapq.heappush(new_genome, new_de)
        return new_genome

    def generate_children(self, other):
        # STUDENT How does this work?  Explain it in your writeup.
        if len(self.genome) > 0:
            pa = random.randint(0, len(self.genome) - 1)
        else:
            pa = 0
        if len(other.genome) > 0:
            pb = random.randint(0, len(other.genome) - 1)
        else:
            pb = 0
            
        a_part = self.genome[:pa] if len(self.genome) > 0 else []
        b_part = other.genome[pb:] if len(other.genome) > 0 else []
        ga = a_part + b_part
        b_part = other.genome[:pb] if len(other.genome) > 0 else []
        a_part = self.genome[pa:] if len(self.genome) > 0 else []
        gb = b_part + a_part
        # do mutation
        return Individual_DE(self.mutate(ga)), Individual_DE(self.mutate(gb))

    # Apply the DEs to a base level.
    def to_level(self):
        if self._level is None:
            base = Individual_Grid.empty_individual().to_level()
            for de in sorted(self.genome, key=lambda de: (de[1], de[0], de)):
                # de: x, type, ...
                x = de[0]
                de_type = de[1]
                if de_type == "4_block":
                    y = de[2]
                    breakable = de[3]
                    base[y][x] = "B" if breakable else "X"
                elif de_type == "5_qblock":
                    y = de[2]
                    has_powerup = de[3]  # boolean
                    base[y][x] = "M" if has_powerup else "?"
                elif de_type == "3_coin":
                    y = de[2]
                    base[y][x] = "o"
                elif de_type == "7_pipe":
                    h = de[2]
                    base[height - h - 1][x] = "T"
                    for y in range(height - h, height):
                        base[y][x] = "|"
                elif de_type == "0_hole":
                    w = de[2]
                    for x2 in range(w):
                        base[height - 1][clip(1, x + x2, width - 2)] = "-"
                elif de_type == "6_stairs":
                    h = de[2]
                    dx = de[3]  # -1 or 1
                    for x2 in range(1, h + 1):
                        for y in range(x2 if dx == 1 else h - x2):
                            base[clip(0, height - y - 1, height - 1)][clip(1, x + x2, width - 2)] = "X"
                elif de_type == "1_platform":
                    w = de[2]
                    h = de[3]
                    madeof = de[4]  # from "?", "X", "B"
                    for x2 in range(w):
                        base[clip(0, height - h - 1, height - 1)][clip(1, x + x2, width - 2)] = madeof
                elif de_type == "2_enemy":
                    base[height - 2][x] = "E"
            self._level = base
        return self._level

    @classmethod
    def empty_individual(_cls):
        # STUDENT Maybe enhance this
        g = []
        return Individual_DE(g)

    @classmethod
    def random_individual(_cls):
        # STUDENT Maybe enhance this
        elt_count = random.randint(8, 128)
        g = [random.choice([
            (random.randint(1, width - 2), "0_hole", random.randint(1, 8)),
            (random.randint(1, width - 2), "1_platform", random.randint(1, 8), random.randint(0, height - 1), random.choice(["?", "X", "B"])),
            (random.randint(1, width - 2), "2_enemy"),
            (random.randint(1, width - 2), "3_coin", random.randint(0, height - 1)),
            (random.randint(1, width - 2), "4_block", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "5_qblock", random.randint(0, height - 1), random.choice([True, False])),
            (random.randint(1, width - 2), "6_stairs", random.randint(1, height - 4), random.choice([-1, 1])),
            (random.randint(1, width - 2), "7_pipe", random.randint(2, height - 4))
        ]) for i in range(elt_count)]
        return Individual_DE(g)


Individual = Individual_Grid


def generate_successors(population):
    results = []
    fitness_range = []
    # STUDENT Design and implement this
    # Hint: Call generate_children() on some individuals and fill up results.
    best = 0
    
    # do half tournament_selection
    while len(results) < len(population)/2 + 1:
        tournament_parent1 = tournament_selection(population, 2)
        tournament_parent2 = tournament_selection(population, 2)
        results += tournament_parent1.generate_children(tournament_parent2)
        
    
    # other half roulette_selection
    roulette_parent1 = None
    roulette_parent2 = None
    while len(results) < len(population):
        float1 = random.uniform(0, 1)
        float2 = random.uniform(0, 1)
        fitness_range = roulette_selection(population)
        
        for i in range(len(fitness_range)):
            if float1 < fitness_range[i]:
                roulette_parent1 = population[i]
            if float2 < fitness_range[i]:
                roulette_parent2 = population[i]
        results += roulette_parent1.generate_children(roulette_parent2)
        
    return results


def roulette_selection(population):
    fitness_sum = sum(map(Individual.fitness, population))
    previous_score = 0.0
    roulette = []
    for i in population:
        previous_score = previous_score + i.fitness() / fitness_sum
        roulette.append(previous_score)
        
    return roulette
    
def tournament_selection(population, x):
    winning_pop = None
    for i in range(0, x):
        random_population = population[random.randint(0, len(population) - 1)]  
        if winning_pop == None or random_population.fitness() > winning_pop.fitness():
            winning_pop = random_population
            
    return winning_pop





def ga():
    # STUDENT Feel free to play with this parameter
    pop_limit = 480
    # Code to parallelize some computations
    batches = os.cpu_count()
    if pop_limit % batches != 0:
        print("It's ideal if pop_limit divides evenly into " + str(batches) + " batches.")
    batch_size = int(math.ceil(pop_limit / batches))
    with mpool.Pool(processes=os.cpu_count()) as pool:
        init_time = time.time()
        # STUDENT (Optional) change population initialization
        population = [Individual.random_individual() if random.random() < 0.9
                      else Individual.empty_individual()
                      for _g in range(pop_limit)]
        # But leave this line alone; we have to reassign to population because we get a new population that has more cached stuff in it.
        population = pool.map(Individual.calculate_fitness,
                              population,
                              batch_size)
        #print('population: ', population)
        init_done = time.time()
        print("Created and calculated initial population statistics in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        now = start
        print("Use ctrl-c to terminate this loop manually.")
        try:
            while True:
                now = time.time()
                # Print out statistics
                if generation > 0:
                    best = max(population, key=Individual.fitness)
                    print("Generation:", str(generation))
                    print("Max fitness:", str(best.fitness()))
                    print("Average generation time:", (now - start) / generation)
                    print("Net time:", now - start)
                    with open("levels_last.txt", 'w') as f:
                        for row in best.to_level():
                            f.write("".join(row) + "\n")
                generation += 1
                # STUDENT Determine stopping condition
                #stops if fitness is over this threshold
                if max(population, key=Individual.fitness).fitness() > 6:
                    break
                # STUDENT Also consider using FI-2POP as in the Sorenson & Pasquier paper
                gentime = time.time()
                next_population = generate_successors(population)
                gendone = time.time()
                print("Generated successors in:", gendone - gentime, "seconds")
                # Calculate fitness in batches in parallel
                next_population = pool.map(Individual.calculate_fitness,
                                           next_population,
                                           batch_size)
                popdone = time.time()
                print("Calculated fitnesses in:", popdone - gendone, "seconds")
                population = next_population
        except KeyboardInterrupt:
            pass
    return population


if __name__ == "__main__":
    final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
    best = final_gen[0]
    print("Best fitness: " + str(best.fitness()))
    now = time.strftime("%m_%d_%H_%M_%S")
    # STUDENT You can change this if you want to blast out the whole generation, or ten random samples, or...
    for k in range(0, 1):
        #print(k)
        with open("levels_" + now + "_" + str(k) + ".txt", 'w') as f:
            for row in final_gen[k].to_level():
                f.write("".join(row) + "\n")
