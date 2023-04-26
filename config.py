import argparse

NUM_RIDERS = 3500
MEAN_SPAWN_RATE = 2.38

BIKES_PER_STATION = 10

START_STATION_PROBS_FILE = "./data/start_station_probs.csv"
TRIP_STATS_FILE = "./data/trip_stats.csv"

END_TIME = 1440


def make_parser():
    parser = argparse.ArgumentParser(description="Run a bike share simulation")

    parser.add_argument(
        "--num-riders",
        "-r",
        default=NUM_RIDERS,
        type=int,
        help="The number of riders that spawn in the time frame of the simulation.",
    )
    parser.add_argument(
        "--mean-spawn-rate",
        "-s",
        default=MEAN_SPAWN_RATE,
        type=float,
        help="The mean of the exponential distribution for the spawn rate of the riders (in riders/min).",
    )

    parser.add_argument(
        "--bikes-per-stations",
        "-b",
        default=BIKES_PER_STATION,
        type=int,
        help="The number of bikes per station. Specify -1 for infinite bikes per station.",
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

    return parser