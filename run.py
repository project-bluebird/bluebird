"""
Entry point for the BlueBird app
"""

import argparse
from typing import Any, Dict

from dotenv import load_dotenv

from bluebird import BlueBird
from bluebird.settings import Settings
from bluebird.utils.properties import SimType, SimMode

_ARG_BOOL_ACTION = "store_true"


def _parse_args() -> Dict[str, Any]:
    """
    Parse CLI arguments and override any default settings
    :return:
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sim-type",
        type=str,
        help=f"The type of simulator to connect to. Supported values are: "
        f'{", ".join([x.name for x in SimType])}',
    )
    parser.add_argument(
        "--sim-host", type=str, help="Hostname or IP of the simulator to connect to"
    )
    parser.add_argument(
        "--reset-sim",
        action=_ARG_BOOL_ACTION,
        help="Resets the simulation on connection",
    )
    parser.add_argument("--log-rate", type=float, help="Log rate in sim-seconds")
    parser.add_argument(
        "--sim-mode",
        type=str,
        help="Set the initial mode. Supported values are: "
        f'{", ".join([x.name for x in SimMode])}',
    )
    parser.add_argument(
        "--disable-stream",
        action=_ARG_BOOL_ACTION,
        help="Disables automatic streaming of the simulator state to BlueBird",
    )
    args = parser.parse_args()

    if args.sim_type:
        Settings.set_sim_type(args.sim_type)

    if args.sim_host:
        Settings.SIM_HOST = args.sim_host

    if args.log_rate:
        if args.log_rate < 0:
            raise ValueError("Rate must be positive")
        Settings.SIM_LOG_RATE = args.log_rate

    if args.sim_mode:
        Settings.set_sim_mode(args.sim_mode)

    if args.disable_stream:
        Settings.STREAM_ENABLE = False

    return vars(args)


def main():
    """
    Main app entry point
    :return:
    """

    args = _parse_args()
    load_dotenv(verbose=True, override=True)

    with BlueBird(args) as app:
        app.setup_sim_client()
        if app.connect_to_sim():
            # Run the Flask app. Blocks here until it exits
            app.run()


if __name__ == "__main__":
    main()
