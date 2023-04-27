# BikeShareSimulation

Team Member: Rishav Bhagat Team Number: 7

Report File: pdfs/report.pdf

Code Organization:

args_util.py: Argument util file that adds functionality to the parser to get arguments from the command line or json/yaml config files.

config.py: Contains the make_parser function and all the default arguments from the pdf for the simulation.

simulation.py: The discrete event simulation code. This includes the initialization of the simulation through loading of the data files and also the actual simulation code in the run function. Within the run function, there are inner functions for all the events, the scheduler, and other utility functions.

main.py: The main entry point that does one run of the simulation given the arguments/configuration of the simulation and then prints and saves the results.

confidence_intervals.py: This runs the simulation N times and then grabs all the estimates from the reports sub dictionary of the results of the simulation (includes the two values asked for in the project pdf). Then, a bunch of values are calculated over these N runs including mean, standard deviation, standard error, and a 90% confidence interval. The confidence and N values can be changed through the config file or argparse arguments.