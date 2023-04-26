import csv
import numpy as np


class Simulation:
    def __init__(
        self,
        num_riders=3500,
        mean_spawn_rate=2.38,
        bikes_per_station=10,
        ride_time_mean=2.78,
        ride_time_std=0.619,
        start_station_probs_file="./data/start_station_probs.csv",
        trip_stats_file="./data/trip_stats.csv",
        end_time=1440,
        **_,
    ) -> None:
        self.n = num_riders
        self.lambda_ = mean_spawn_rate

        self.k = bikes_per_station

        self.mu = ride_time_mean
        self.sigma = ride_time_std

        self.stations, self.p = self.load_start_probabilities(
            start_station_probs_file=start_station_probs_file
        )
        self.m = len(self.stations)
        self.stations_mapping = self.build_stations_mapping(self.stations)

        self.q = self.load_trip_stats(trip_stats_file=trip_stats_file)

        self.end_time = end_time

    def load_start_probabilities(self, start_station_probs_file):
        stations = []
        p = []
        with open(start_station_probs_file) as f:
            reader = csv.reader(f)
            _ = next(reader)
            for row in reader:
                name, prob = row
                stations.append(name)
                p.append(float(prob))
        return np.array(stations), np.array(p)
    
    def build_stations_mapping(self, stations):
        mapping = {}
        for i in range(len(stations)):
            mapping[stations[i]] = i
        return mapping
    
    def load_trip_stats(self, trip_stats_file):
        q = np.zeros((self.m, self.m))
        with open(trip_stats_file) as f:
            reader = csv.reader(f)
            _ = next(reader)
            for row in reader:
                start, end, count, _, _ = row
                i = self.stations_mapping[start]
                j = self.stations_mapping[end]
                q[i, j] += int(count)
        q_sum = np.sum(q, axis=1).reshape(-1, 1)
        q = q / q_sum
        return q


    def run(self):
        print(self.p)
        print(self.q)
        print(self.stations)