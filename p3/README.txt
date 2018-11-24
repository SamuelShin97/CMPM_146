Samuel Shin, sayshin@ucsc.edu, 1510580
Partner: Carlos del Rey, cdelreyg@ucsc.edu, 1710268

This folder contains the following files:

mcts_vanilla.py: vanilla implementation of mcts 
mcts_vanilla_timer.py: vanilla implementation of mcts with a timer (for experiment 3)
mcts_modified.py: modified implementation of mcts (description below)
mcts_modified_timer.py: modified implementation of mcts with a timer (for experiment 3)
experiment1.png: plot for experiment1
experiment1.txt: description of our first experiment
experiment2.txt: description of our second experiment
experiment3.txt: description of our third experiment (for extra credit)

Our modified version includes sensitivity to draws and losses. Vanilla counted both as 0, but the modified version distinguishes between them (draw = 0 and loss = -1). This seems to lead to a better gameplay because now the algorithm prefers a draw over a loss. We know that this is a simple modification, but we wanted to show that even a slight change in the information could be crucial.