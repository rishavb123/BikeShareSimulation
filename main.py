from args_utils import get_args
from config import make_parser
from simulation import Simulation

def main():
    args = get_args(make_parser(), configs_root="./configs/")
    s = Simulation(**vars(args))
    s.run()

if __name__ == "__main__":
    main()