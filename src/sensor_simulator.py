"""
sensor_simulator.py

Generates a time-varying battery State of Charge (SoC) value and publishes it
into the Kuksa Databroker under its VSS path. This stands in for a real
in-vehicle battery sensor / BMS reading.

Requires: kuksa-client  (pip install kuksa-client)
"""

import os
import time
import random

from kuksa_client.grpc import VSSClient, Datapoint

VSS_PATH = "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current"

KUKSA_HOST = os.environ.get("KUKSA_HOST", "localhost")
KUKSA_PORT = int(os.environ.get("KUKSA_PORT", "55555"))

SCENARIO = os.environ.get("SCENARIO", "drain_and_recover")


def drain_and_recover_sequence():
    for soc in range(40, 7, -1):
        yield soc
    for soc in range(8, 26):
        yield soc


def steady_sequence():
    while True:
        yield 50 + random.randint(-2, 2)


def main():
    sequence = (
        drain_and_recover_sequence()
        if SCENARIO == "drain_and_recover"
        else steady_sequence()
    )

    with VSSClient(KUKSA_HOST, KUKSA_PORT) as client:
        for soc in sequence:
            client.set_current_values({VSS_PATH: Datapoint(float(soc))})
            print(f"[sensor_simulator] published {VSS_PATH} = {soc}%")
            time.sleep(2)

    print("[sensor_simulator] scenario complete")


if __name__ == "__main__":
    main()
