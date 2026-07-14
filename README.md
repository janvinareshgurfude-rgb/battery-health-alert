# Battery Health Alert -- SDV Pipeline (Iteration 1: Baseline Implementation)

Group HAG

## Overview

This repository implements a baseline Software-Defined Vehicle (SDV) data pipeline that carries a simulated battery State of Charge (SoC) signal from a simulated sensor through to a digital twin, and demonstrates the twin updating live as new readings arrive.

Sensor Simulator -> Eclipse Kuksa (VSS abstraction) -> Kuksa+eCAL+Ditto pipeline service -> Eclipse Ditto (digital twin) -> Alert-Monitor

Eclipse openDuT is used alongside the pipeline (not in the primary data path) to repeatedly drive the low-battery scenario and check that the pipeline reacts correctly and quickly.

See architecture-diagram.svg and sequence-diagram.svg for the full as-implemented architecture and a runtime sequence diagram, and report.md for the full written report.

## Selected Components and Roles

| Component | Role |
|---|---|
| Eclipse Kuksa (Databroker) | Vehicle-side data abstraction. Exposes the simulated SoC value under its VSS path (Vehicle.Powertrain.TractionBattery.StateOfCharge.Current). |
| Eclipse eCAL | Real-time pub/sub transport layer carrying SoC updates, used inside the combined pipeline service. |
| Eclipse Ditto | Digital twin backend. Holds the battery.soc and battery.batteryAlert properties of the hag:vehicle-01 Thing. |
| Alert-Monitor | Monitoring interface. Polls/observes the Ditto Thing and prints SoC + alert-state transitions. |
| Eclipse openDuT | Test orchestration. Drives repeated low-battery scenarios end-to-end and measures correctness/latency. |

## Required Software

- Docker Desktop (Windows/Mac) or Docker Engine + Compose (Linux)
- Python 3.11 (only if running services outside Docker for local debugging)
- kuksa-client Python package
- Eclipse eCAL Python bindings (built per the eCAL documentation)
- curl (for the Ditto init script)

## Setup on Windows

1. Install WSL2: wsl --install in an admin PowerShell, reboot if prompted.
2. Install Docker Desktop, confirm WSL2 backend is on, enable WSL Integration for Ubuntu.
3. Do everything below inside your Ubuntu (WSL) terminal.
4. This project avoids network_mode: host so it works the same on Windows, Mac, and Linux.

## Installation

docker compose up -d kuksa-databroker mongodb ditto
chmod +x ditto-init.sh
./ditto-init.sh
curl -u ditto:ditto http://localhost:8080/api/2/things/hag:vehicle-01

## Running the Pipeline

docker compose up -d kuksa-ecal-ditto-pipeline alert-monitor
docker compose up sensor-simulator

Watch the alert-monitor logs:

docker compose logs -f alert-monitor

Expected behavior:
1. SoC values print steadily as they drop.
2. When SoC first drops below 15%, batteryAlert transitions to true.
3. As SoC recovers, batteryAlert stays true until SoC rises back above 18% (hysteresis), then transitions back to false.
4. Querying Ditto directly reflects the current soc and batteryAlert values.

## Reproducing the Demonstrated Behavior

docker compose down
docker compose up -d kuksa-databroker mongodb ditto
./ditto-init.sh
docker compose up -d kuksa-ecal-ditto-pipeline alert-monitor
docker compose up sensor-simulator

Set SCENARIO=steady as an environment variable on sensor-simulator to run a flat, non-alerting baseline instead.

## Functional Modification (Iteration 1)

What changed: a hysteresis band was added to the batteryAlert rule. The alert sets at SoC < 15% and only clears once SoC rises above 18%.

Where it lives: src/kuksa_ecal_ditto_pipeline.py, in on_ecal_message(). The pipeline service holds the current alert state in memory and only flips it at the two thresholds.

Effect on pipeline behavior: without this change, a SoC value oscillating near 15% would cause batteryAlert to flap true/false on every reading near the boundary. With hysteresis, each logged transition reflects a real state change, not sensor jitter.

## Evidence of Correct Operation

See evidence/ for logs and API query output captured while running the scenario above.
