import numpy as np
import scipy.stats
import json
import yaml
from tqdm import tqdm

from config import make_parser
from args_utils import get_args
from simulation import Simulation

N_RUNS = 10
CONFIDENCE = 0.9


def main():
    parser = make_parser()
    parser.add_argument(
        "--n-runs",
        "-nr",
        default=N_RUNS,
        type=int,
        help="The number of runs to create the confidence interval over",
    )
    parser.add_argument(
        "--confidence",
        "-cv",
        default=CONFIDENCE,
        type=float,
        help="The confidence value to use to create the two-sided interval",
    )

    args = get_args(parser=parser, configs_root="./ci_configs/")
    vals = {}

    for i in tqdm(range(args.n_runs)):
        s = Simulation(
            num_riders=args.num_riders,
            mean_spawn_rate=args.mean_spawn_rate,
            bikes_per_station=args.bikes_per_station,
            ride_time_mean=args.ride_time_mean,
            ride_time_std=args.ride_time_std,
            start_station_probs_file=args.start_station_probs_file,
            trip_stats_file=args.trip_stats_file,
            end_time=args.end_time,
            num_time_bins=args.num_time_bins,
        )
        stats = s.run()
        for k in stats["report"]:
            if i == 0:
                vals[k] = []
            vals[k].append(stats["report"][k]["estimate"])
    vals = {k: {"raw": np.array(v)} for k, v in vals.items()}

    for k in vals:
        data = vals[k]["raw"]
        vals[k]["mean"] = np.mean(data)
        vals[k]["std"] = np.std(data)
        vals[k]["se"] = scipy.stats.sem(data)
        vals[k]["n"] = len(data)

        se = vals[k]["se"]
        m = vals[k]["mean"]
        n = vals[k]["n"]

        vals[k]["confidence"] = args.confidence
        vals[k]["confidence_interval"] = [*scipy.stats.t.interval(args.confidence, n - 1, loc=m, scale=se)]

        vals[k]["raw"] = list(vals[k]["raw"])

    print(json.dumps(vals, indent=4))

    if args.save_results:
        with open(args.save_results, "w") as f:
            if args.save_results.split(".")[-1] == "json":
                json.dump(vals, f, indent=4)
            else:
                yaml.dump(vals, f, indent=4)


if __name__ == "__main__":
    main()
