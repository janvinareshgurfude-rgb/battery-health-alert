# Battery Health Alert
## Iteration 1: Baseline SDV Pipeline Implementation

Group HAG -- Janvi Gurfude -- YOUR_GROUP_NUMBER

## 1. Overview and Objective

This report documents Iteration 1 of the Battery Health Alert project: a working Software-Defined Vehicle (SDV) pipeline that carries a simulated battery State of Charge (SoC) reading from a simulated sensor through Eclipse Kuksa, Eclipse eCAL, and Eclipse Ditto, and surfaces the resulting vehicle state through a monitoring interface. The objective for this iteration, per the assignment, was system integration: demonstrating that vehicle data can flow end to end from source to digital twin, and that the digital twin's state visibly updates as new readings arrive.

Beyond the baseline pipeline, this iteration also implements one functional modification -- a hysteresis band on the battery alert rule -- described in Section 5.

## 2. Implemented System Architecture

See architecture-diagram.svg for the diagram reflecting the pipeline as implemented, not the originally proposed design.

## 3. Selected Components and Their Roles

| Component | Role in the Implemented Pipeline |
|---|---|
| Eclipse Kuksa (Databroker) | Vehicle-side data abstraction; exposes the simulated SoC reading under its VSS path. |
| Eclipse eCAL | Real-time pub/sub transport layer carrying the SoC reading inside the combined pipeline service. |
| Eclipse Ditto | Digital twin backend; holds the vehicle Thing's battery feature (soc, batteryAlert). |
| Alert-Monitor | Monitoring/visualization interface; polls the Ditto Thing and logs SoC and alert-state transitions. |
| Eclipse openDuT | Test orchestration layer; drives repeated low-battery scenarios and measures correctness/latency. |

## 4. Runtime Data Flow

See sequence-diagram.svg for the sequence diagram showing the runtime interaction for a single reading that triggers an alert.

## 5. Functional Modification: Alert Hysteresis

What changed: the batteryAlert rule was changed from a single 15% threshold to a two-threshold hysteresis band. The alert sets when SoC drops below 15%, but only clears once SoC has recovered above 18%.

Where it lives: in src/kuksa_ecal_ditto_pipeline.py, in on_ecal_message(), which holds the current alert state and only flips it at the appropriate threshold.

Why: without hysteresis, a SoC value hovering near 15% would cause batteryAlert to flap true/false on every reading near the boundary.

Effect on pipeline behavior: with the modification in place, each transition recorded corresponds to a genuine crossing into or out of the low-battery condition.

## 6. Evidence of Correct Operation

The scripted drain-and-recover scenario exercises both the trigger and clear paths. See the evidence/ folder for captured logs and API query output from an actual run.

## 7. Repository and Reproducibility

The full implementation is included in this repository, along with a README describing installation, running, and reproduction steps.

## 8. Next Steps (Iteration 2 Preview)

- Replace the console-based Alert-Monitor with a full dashboard client.
- Automate the openDuT scenario runs and surface pass/fail + latency statistics.
- Move from a JSON-over-eCAL payload to a typed protobuf message.
