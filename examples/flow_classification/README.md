# Example: In-Network Flow Classification on P4Pi + DPDK

This example demonstrates **in-network ML flow classification** using a Decision
Tree model running inside a DPDK software switch on a Raspberry Pi 4.

Instead of sending packets to an external server for classification, the trained
model runs directly in the switch data plane — classifying each packet at line
rate as it passes through.

## What this example does

1. Trains a Decision Tree classifier using Planter
2. Automatically converts the trained model into P4 match-action tables
3. Compiles the P4 program using `p4c --target dpdk` for the DPDK SWX pipeline
4. Loads the model's table entries into a running DPDK pipeline
5. Classifies test packets **inside the switch** and reports accuracy

## Use case

This example uses the Iris dataset as a proxy for network flow features. In a
real deployment, the four features would map to packet header fields — e.g.
source/destination IP prefix bits, protocol, port ranges — enabling lightweight
flow classification at line rate without any external inference server.

## Requirements

- Raspberry Pi 4 (4GB or 8GB) running [P4Pi SIGCOMM2022 image](https://github.com/p4lang/p4pi/releases/tag/sigcomm2022)
- Planter cloned at `~/Planter` (branch: `gsoc-p4c-dpdk`)
- `dpdk_pipeline_build` at `~/dpdk_pipeline_build` (built from `/usr/share/dpdk/examples/pipeline/`)
- Python 3.9+ with dependencies: `pip3 install scikit-learn numpy pandas scapy`

## Quick start

```bash
# 1. Clone and set up (if not already done)
git clone https://github.com/pig8pig/Planter.git ~/Planter
cd ~/Planter && git checkout gsoc-p4c-dpdk

# 2. Build the dpdk-pipeline binary (one time)
cp -r /usr/share/dpdk/examples/pipeline ~/dpdk_pipeline_build
cd ~/dpdk_pipeline_build && make

# 3. Run the example
cd ~/Planter/examples/flow_classification
chmod +x run_flow_classification.sh
./run_flow_classification.sh
```

## Expected output

```
============================================================
 In-Network Flow Classification — Planter on P4Pi + DPDK
============================================================

[1/5] Configuring hugepages...
      OK — 64 x 2MB hugepages allocated

[2/5] Training Decision Tree and generating DPDK P4 pipeline...
      OK — model trained and P4 compiled

[3/5] Training results:
    accuracy    0.9556

[4/5] Running inference on DPDK pipeline...
      (Decision Tree running inside the switch data plane)

[5/5] DPDK Pipeline Results:
    accuracy    0.9556  (matching Python baseline)

============================================================
 Done. Decision Tree inference completed on DPDK switch.
============================================================
```

## Results

| Model | Python baseline | DPDK switch | Match? |
|-------|----------------|-------------|--------|
| Decision Tree (depth=4) | 95.56% | 95.56% | ✅ |

The DPDK pipeline matches the Python baseline exactly, confirming that the
in-network model correctly implements the trained classifier.

## How it works

```
Train (Python)          Generate (Planter)       Compile (p4c-dpdk)
sklearn Decision Tree → P4 match-action tables → DPDK .spec pipeline
        ↓
Load (dpdk-pipeline CLI)          Classify (DPDK SWX)
Table entries → running switch → packets classified at line rate
```

### DPDK 20.11 compatibility notes

This adapter works around several limitations in DPDK 20.11's SWX pipeline:

- **No wildcard/ternary table support** in the text entry format — resolved by
  expanding ternary ranges into exact-match entries using Planter's own matching
  formula `(x & value) == (value & mask)`
- **Missing instructions** (`lookahead`, `drop`) — patched automatically in the
  generated `.spec` file
- **Table size alignment** — sizes must satisfy `n/4 = power of 2` for correct
  hash bucket addressing; computed automatically from actual entry counts

## Extending this example

To use your own dataset and model:

```bash
# Run Planter in interactive mode
cd ~/Planter
python3 Planter.py -m
# Select: model=DT, type=EB, your dataset, architecture=psa, device=dpdk, type=software
```

See `src/targets/dpdk/software/run_model.py` for the full adapter implementation.