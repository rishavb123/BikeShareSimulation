import argparse

NUM_RIDERS = 3500
MEAN_SPAWN_RATE = 2.38

BIKES_PER_STATION = 10

RIDE_TIME_MEAN = 2.78
RIDE_TIME_STD = 0.619

START_STATION_PROBS_FILE = "./data/start_station_probs.csv"
TRIP_STATS_FILE = "./data/trip_stats.csv"

END_TIME = 1440
NUM_TIME_BINS = 24

SAVE_RESULTS = None


def make_parser():
    parser = argparse.ArgumentParser(description="Run a bike share simulation")

    parser.add_argument(
        "--num-riders",
        "-n",
        default=NUM_RIDERS,
        type=int,
        help="The number of riders that spawn in the time frame of the simulation.",
    )
    parser.add_argument(
        "--mean-spawn-rate",
        "-l",
        default=MEAN_SPAWN_RATE,
        type=float,
        help="The mean of the exponential distribution for the spawn rate of the riders (in riders/min).",
    )

    parser.add_argument(
        "--bikes-per-station",
        "-k",
        default=BIKES_PER_STATION,
        type=lambda s: float(s) if s == 'inf' else int(s),
        help="The number of bikes per station. Specify inf for infinite bikes per station.",
    )

    parser.add_argument(
        "--ride-time-mean",
        "-mu",
        default=RIDE_TIME_MEAN,
        type=float,
        help="The log mean ride time, which is log normally distributed with the mean specified in this parameter.",
    )
    parser.add_argument(
        "--ride-time-std",
        "-s",
        default=RIDE_TIME_STD,
        type=float,
        help="The log std ride time, which is log normally distributed with standard deviation specified in this parameter.",
    )

    parser.add_argument(
        "--start-station-probs-file",
        "-p",
        default=START_STATION_PROBS_FILE,
        type=str,
        help="The csv file containing all the stations and the probabilities of starting in that station.",
    )
    parser.add_argument(
        "--trip-stats-file",
        "-t",
        default=TRIP_STATS_FILE,
        type=str,
        help="The csv file containing the trip statistics that will be used to calculate transition probabilities",
    )

    parser.add_argument(
        "--end-time",
        "-e",
        default=END_TIME,
        type=int,
        help="The end time of the simulation (starting from t=0) in minutes.",
    )
    parser.add_argument(
        "--num-time-bins",
        "-b",
        default=NUM_TIME_BINS,
        type=int,
        help="The number of time bins to include in the results."
    )

    parser.add_argument(
        "--save-results",
        "-sr",
        default=SAVE_RESULTS,
        type=str,
        help="The file in which to save the results of the simulation to.",
    )

    return parser
