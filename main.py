import json

from args_utils import get_args
from config import make_parser
from simulation import Simulation

def main():
    args = get_args(make_parser(), configs_root="./configs/")
    s = Simulation(
        num_riders=args.num_riders,
        mean_spawn_rate=args.mean_spawn_rate,
        bikes_per_station=args.bikes_per_station,
        ride_time_mean=args.ride_time_mean,
        ride_time_std=args.ride_time_std,
        start_station_probs_file=args.start_station_probs_file,
        trip_stats_file=args.trip_stats_file,
        end_time=args.end_time,
        save_results=args.save_results,
    )
    print(json.dumps(s.run(), indent=4))

if __name__ == "__main__":
    main()