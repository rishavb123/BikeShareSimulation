from collections import deque
import csv
import numpy as np
import json
import yaml


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
        save_results=None,
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

        self.save_results = save_results

        self.ran = False
        self.stats = {}

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
            stations.append("dump")
            p.append(0)
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
                i = self.stations_mapping.get(start, self.stations_mapping["dump"])
                j = self.stations_mapping.get(end, self.stations_mapping["dump"])
                q[i, j] += int(count)
        q_sum = np.sum(q, axis=1).reshape(-1, 1)
        q_sum[q_sum == 0] = 1
        q = q / q_sum
        return q

    def run(self):
        if self.ran:
            return

        # setup stats
        self.stats["stations_mapping"] = self.stations_mapping
        self.stats["start_probabilities"] = {i: self.p[i] for i in range(self.m)}
        self.stats["transition_probabilities"] = {
            f"{i} -> {j}": self.q[i, j] for i in range(self.m) for j in range(self.m)
        }
        self.stats["total_riders"] = 0
        self.stats["invocations"] = {}

        # create global variables
        bikes_stations = [self.k for _ in range(self.m)]
        riders_waiting = [0 for _ in range(self.m)]

        # define event system
        events = [deque() for _ in range(self.end_time)]

        def count_invocation_and_args(invoc_dict, kwargs):
            # Count invocations
            invoc_dict["total"] += 1

            # Count arg values
            for k, v in kwargs.items():
                if k == "t":
                    continue
                if k not in invoc_dict["args"]:
                    invoc_dict["args"][k] = {}
                invoc_dict["args"][k][v] = invoc_dict["args"][k].get(v, 0) + 1

        def event_wrapper(f, **kwargs):
            func_kwargs = {
                key: kwargs[key] for key in kwargs if key in f.__code__.co_varnames
            }

            def wrapper():
                if f.__name__ not in self.stats["invocations"]:
                    self.stats["invocations"][f.__name__] = {
                        "total": 0,
                        "ret_vals": {},
                        "args": {},
                        "overtime": {"total": 0, "args": {}},
                    }
                ret = f(**func_kwargs)

                count_invocation_and_args(
                    self.stats["invocations"][f.__name__], func_kwargs
                )

                # Count return values
                if ret is not None:
                    self.stats["invocations"][f.__name__]["ret_vals"][ret] = (
                        self.stats["invocations"][f.__name__]["ret_vals"].get(ret, 0)
                        + 1
                    )

            return wrapper

        def schedule(event, t, num_times=1, important=False, **kwargs):
            kwargs["t"] = t
            if t >= self.end_time:
                if event.__name__ not in self.stats["invocations"]:
                    self.stats["invocations"][event.__name__] = {
                        "total": 0,
                        "ret_vals": {},
                        "args": {},
                        "overtime": {"total": 0, "args": {}},
                    }
                func_kwargs = {
                    key: kwargs[key]
                    for key in kwargs
                    if key in event.__code__.co_varnames
                }
                count_invocation_and_args(
                    self.stats["invocations"][event.__name__]["overtime"], func_kwargs
                )
                return
            argless_event = event_wrapper(event, **kwargs)
            for _ in range(num_times):
                if important:
                    events[t].appendleft(argless_event)
                else:
                    events[t].append(argless_event)

        # define events
        def event__spawn_rider(t):
            if self.stats["total_riders"] < self.n:
                self.stats["total_riders"] += 1
                i = np.random.choice(self.m, p=self.p)
                riders_waiting[i] += 1
                schedule(event__wait_for_bike, t, i=i)
                return i
            return "Limited"

        def event__wait_for_bike(t, i):
            if bikes_stations[i] > 0:
                schedule(event__take_bike, t, important=True, i=i)
                return "Take"
            else:
                schedule(event__wait_for_bike, t + 1, i=i)
                return "Wait"

        def event__take_bike(t, i):
            if bikes_stations[i] <= 0:
                schedule(event__wait_for_bike, t, i=i)
            bikes_stations[i] -= 1
            s = np.random.normal(loc=self.mu, scale=self.sigma)
            ride_time = np.round(np.exp(s))
            schedule(event__return_bike, t + int(ride_time), important=True, i=i)

        def event__return_bike(i):
            j = np.random.choice(self.m, p=self.q[i])
            bikes_stations[j] += 1
            return j

        # define simulation event caller
        def run_events(t):
            while len(events[t]) > 0:
                events[t].popleft()()
            events[t] = None

        # schedule spawn events
        num_spawn = np.round(
            np.random.exponential(scale=self.lambda_, size=(self.end_time,))
        )
        [
            schedule(event__spawn_rider, t, int(num_spawn[t]))
            for t in range(self.end_time)
        ]

        # run simulation loop
        for t in range(self.end_time):
            run_events(t)

        # simulation validation checks
        self.stats["validation"] = {
            "spawn_stations": {
                "expected": {
                    **{
                        i: self.p[i] * self.stats["total_riders"] for i in range(self.m)
                    },
                    "Limited": max(0, self.lambda_ * self.end_time - self.n),
                },
                "simulated": self.stats["invocations"]["event__spawn_rider"][
                    "ret_vals"
                ],
            },
            "return_bike": {
                "expected": {
                    j: np.sum(
                        [
                            self.q[i, j]
                            * (
                                self.stats["invocations"]["event__take_bike"]["args"][
                                    "i"
                                ].get(i, 0)
                                - self.stats["invocations"]["event__return_bike"][
                                    "overtime"
                                ]["args"]
                                .get("i", {})
                                .get(i, 0)
                            )
                            for i in range(self.m)
                        ]
                    )
                    for j in range(self.m)
                },
                "simulated": self.stats["invocations"]["event__return_bike"][
                    "ret_vals"
                ],
            },
        }

        for validation_check in self.stats["validation"]:
            self.stats["validation"][validation_check]["error"] = {
                k: self.stats["validation"][validation_check]["simulated"].get(k, 0)
                - self.stats["validation"][validation_check]["expected"][k]
                for k in self.stats["validation"][validation_check]["expected"]
            }

        # save stats
        if self.save_results is not None:
            with open(self.save_results, "w") as f:
                if self.save_results.split(".")[-1] == "json":
                    json.dump(self.stats, f, indent=4)
                else:
                    yaml.dump(self.stats, f, indent=4)

        # return
        self.ran = True
        return self.stats
