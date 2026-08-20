# Example: In-Network Anomaly Detection on P4Pi + DPDK

This example demonstrates **in-network anomaly/intrusion detection** using a
Random Forest model running inside a DPDK software switch on a Raspberry Pi 4.

The Random Forest classifier runs entirely in the switch data plane — flagging
anomalous traffic patterns at line rate as packets pass through, without any
round-trip to an external detection server.

## What this example does

1. Trains a Random Forest classifier (5 trees) using Planter
2. Converts the ensemble model into P4 match-action tables (10 tables total:
   4 feature lookup + 5 per-tree leaf tables + 1 voting/decision table)
3. Compiles and runs the pipeline on DPDK
4. Classifies test packets inside the switch and reports accuracy

## Use case

Random Forest is widely used in real intrusion detection systems for its
accuracy and interpretability. This example shows how a trained RF can run
directly in the network switch — classifying flows as normal/attack types
before they even reach the host, with sub-microsecond latency per packet.

## Requirements

Same as the flow classification example. See `examples/flow_classification/README.md`.

## Quick start

```bash
cd ~/Planter
# Switch to RF model
python3 -c "
import json
c = json.load(open('src/configs/Planter_config.json'))
c['model config']['model'] = 'RF'
json.dump(c, open('src/configs/Planter_config.json', 'w'), indent=4)
"
PLANTER_FORCE_GENERATE_ENTRIES=1 python3 Planter.py
```

## Results

| Model | Trees | Python baseline | DPDK switch |
|-------|-------|----------------|-------------|
| Random Forest (depth=4) | 5 | 93.33% | 91.11% |

The 2% gap between Python and DPDK baselines reflects the ternary-to-exact
range expansion approximation — a known, expected effect of DPDK 20.11's
exact-match-only table constraint.

## How Random Forest differs from Decision Tree on DPDK

RF requires a two-stage pipeline not present in the DT adapter:

```
Feature lookup tables (4)     Per-tree leaf tables (5)    Decision table (1)
feature0 range → code_f0  →  tree0: codes → vote0    →  votes → final class
feature1 range → code_f1  →  tree1: codes → vote1
feature2 range → code_f2  →  tree2: codes → vote2
feature3 range → code_f3  →  tree3: codes → vote3
                           →  tree4: codes → vote4
```

Each tree independently classifies the input codes, then the decision table
takes a majority vote across all 5 trees to produce the final class.

## DPDK 20.11 notes

RF leaf tables use DPDK's bit-sliced key extraction — the compiler extracts
specific bits from each feature code for the leaf table lookup keys. The
entry generator correctly applies these bit transformations to match the
compiled pipeline's expected key format.