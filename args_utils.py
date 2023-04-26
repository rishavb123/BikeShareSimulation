from typing import Callable, TextIO, Dict

import argparse
import json
import yaml

supported_exts_loaders = {
    "json": json.load,
    "yml": yaml.safe_load,
    "yaml": yaml.safe_load,
}

supported_exts = list(supported_exts_loaders.keys())


def add_custom_loader(ext: str, loader: Callable[[TextIO], Dict]) -> None:
    """Add a custom loader for a specific type of config file
    Args:
        ext (str): The extension type.
        loader (Callable[[TextIO], Dict]): The loader for the extension type.
    """
    global supported_exts_loaders
    supported_exts_loaders[ext] = loader
    supported_exts.append(ext)


def __clear_defaults(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Clears the default values from a parser and sets them to argparse.SUPPRESS.
    Args:
        parser (argparse.ArgumentParser): The parser to clear defaults of.
    Returns:
        argparse.ArgumentParser: The parser with cleared defaults.
    """
    for action in parser._actions:
        action.default = argparse.SUPPRESS
    return parser


def get_args(
    parser: argparse.ArgumentParser,
    configs_root: str = "",
    default_ext: str = "json",
) -> argparse.Namespace:
    """Gets the arguments from an argparse parser with the added functionality of being able to use a config file. The parser load arguments in the following priority (for each argument it will go down the list until a value is found):
           - Command line arguments
           - Config files ordered from first listed to last listed
           - Parser default values
    Args:
        parser (argparse.ArgumentParser): The argument parser to use (will be modified, do not use after this method)
        configs_root (str, optional): The root to use for the config files. Defaults to "".
        default_ext (str, optional): The default extension to use if none is specified. Defaults to "json".
    Returns:
        argparse.Namespace: returns the parsed arguments.
    """

    parser.add_argument(
        "--config-file",
        "-c",
        default=[],
        type=str,
        nargs="+",
        help=f"A config file specifying some new default arguments (that can be overridden by command line args). This can be a list of config files ({'/'.join(supported_exts)}) with whatever arguments are set in them in order of lowest to highest priority. Usage: --config-file configs/test.json configs/test2.json.",
    )

    args = parser.parse_args()

    args_dict = vars(args)
    cfg_files = list(reversed(args.config_file))

    if configs_root.endswith("/"):
        configs_root = configs_root[:-1]

    for cfg_file in cfg_files:
        cfg_file_name = cfg_file
        if not any(cfg_file_name.endswith(f".{ext}") for ext in supported_exts):
            cfg_file_name += f".{default_ext}"
        with open(f"{configs_root}/{cfg_file_name}") as f:
            ext = cfg_file_name.split(".")[-1]
            if ext not in supported_exts:
                raise NotImplementedError(f"Extension {ext} is not supported")
            configs_dict = supported_exts[ext](f)
            args_dict.update(configs_dict)

    parser = __clear_defaults(parser)

    set_args_dict = vars(parser.parse_args())
    args_dict.update(set_args_dict)

    return args