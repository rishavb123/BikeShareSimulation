import csv
import numpy as np


class Simulation:
    def __init__(
        self,
        num_riders=3500,
        mean_spawn_rate=2.38,
        bikes_per_station=10,
        start_station_probs_file="./data/start_station_probs.csv",
        trip_stats_file="./data/trip_stats.csv",
        end_time=1440,
        **kwargs,
    ) -> None:
        self.n = num_riders
        self.lambda_ = mean_spawn_rate

        self.k = bikes_per_station

        self.stations, self.p_i = self.load_start_probabilities(
            start_station_probs_file
        )
        self.m = len(self.stations)


        self.end_time = end_time

    def load_start_probabilities(self, start_station_probs_file):
        stations = []
        p_i = []
        with open(start_station_probs_file) as f:
            reader = csv.reader(f)
            _ = next(reader)
            for row in reader:
                name, p = row
                stations.append(name)
                p_i.append(float(p))
        return stations, p_i
    
    def run(self):
        print(self.m)