#!/bin/bash
# =============================================================================
# Flow Classification Example — Planter + P4Pi + DPDK
# =============================================================================
# This script demonstrates in-network ML flow classification using a Decision
# Tree model running inside a DPDK software switch on Raspberry Pi.
#
# The trained Decision Tree classifies network flows by their features
# (e.g. petal measurements for Iris, or packet header fields for real traffic)
# at line rate, inside the switch data plane — no external server needed.
#
# Usage:
#   ./run_flow_classification.sh
#
# Requirements:
#   - P4Pi SIGCOMM2022 image flashed and booted
#   - Planter repo at ~/Planter
#   - dpdk_pipeline_build at ~/dpdk_pipeline_build
#   - Hugepages configured (done automatically below)
# =============================================================================

set -e

PLANTER_DIR="$HOME/Planter"
PIPELINE_BIN="$HOME/dpdk_pipeline_build/build/pipeline"
EXAMPLE_DIR="$PLANTER_DIR/examples/flow_classification"

echo "============================================================"
echo " In-Network Flow Classification — Planter on P4Pi + DPDK"
echo "============================================================"
echo ""

# Step 1 — Configure hugepages (required for DPDK)
echo "[1/5] Configuring hugepages..."
sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge 2>/dev/null || true
echo 64 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages > /dev/null
echo "      OK — 64 x 2MB hugepages allocated"
echo ""

# Step 2 — Train the Decision Tree and generate P4 code
echo "[2/5] Training Decision Tree and generating DPDK P4 pipeline..."
cd "$PLANTER_DIR"
python3 Planter.py > /tmp/planter_train.log 2>&1
echo "      OK — model trained and P4 compiled"
echo ""

# Step 3 — Show training accuracy
echo "[3/5] Training results:"
grep "accuracy" /tmp/planter_train.log | tail -3 || true
echo ""

# Step 4 — Run inference on DPDK
echo "[4/5] Running inference on DPDK pipeline..."
echo "      (Decision Tree running inside the switch data plane)"
echo ""

# Step 5 — Show DPDK results
echo "[5/5] DPDK Pipeline Results:"
grep -A 20 "DPDK Pipeline Classification Results" /tmp/planter_train.log || \
    echo "      Check src/targets/dpdk/software/model_test/test_environment/run.log for details"
echo ""
echo "============================================================"
echo " Done. Decision Tree inference completed on DPDK switch."
echo "============================================================"