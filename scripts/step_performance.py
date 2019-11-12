"""
Measures the performance of the STEP endpoint
"""

import argparse
import time

import requests


API_URL_BASE = f"http://localhost:5001/api/v1"


def measure_step(max_steps, multiplier):
    """
	Measure the performance of STEP
	:param max_steps:
	:param multiplier:
	:return:
	"""

    resp = requests.post(f"{API_URL_BASE}/ic", json={"filename": "TEST.scn"})
    assert resp.status_code == 200, "Expected the scenario to be loaded"

    resp = requests.post(f"{API_URL_BASE}/dtmult", json={"multiplier": multiplier})
    assert resp.status_code == 200, "Expected DTMULT to be set"

    times = []
    n_steps = 0

    try:
        while True:
            print(f"Step {n_steps + 1}")

            start = time.time()

            resp = requests.post(f"{API_URL_BASE}/step")
            assert resp.status_code == 200, "Expected the simulation was stepped"

            times.append(time.time() - start)

            n_steps += 1

            if n_steps >= max_steps:
                break

    except KeyboardInterrupt:
        print("Cancelled")

    if not times:
        print("No data collected")
        return

    print(f"times: {times}")
    print(f"Mean step time {sum(times)/float(len(times)):.2f}s (dtmult={multiplier})")


def main():
    """
	Main
	:return:
	"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--max_steps", type=int, default=5)
    args = parser.parse_args()

    for mult in range(6):
        measure_step(args.max_steps, 10 + mult * 10)


if __name__ == "__main__":
    main()
