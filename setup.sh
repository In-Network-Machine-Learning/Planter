#!/bin/bash
# =============================================================================
# Planter + P4Pi + DPDK Setup Script
# GSoC 2026 — Project 3.3
# =============================================================================
# One-command setup for running Planter with the p4c-dpdk target on P4Pi.
#
# Usage:
#   chmod +x setup.sh && ./setup.sh
#
# Tested on: P4Pi SIGCOMM2022 image, Raspberry Pi 4 (4GB/8GB), Python 3.9
# =============================================================================

set -e

PLANTER_DIR="$HOME/Planter"
PIPELINE_BUILD_DIR="$HOME/dpdk_pipeline_build"

echo "========================================================"
echo " Planter + P4Pi + DPDK Setup"
echo "========================================================"
echo ""

# Step 1 — System packages
echo "[1/6] Installing system packages..."
sudo apt-get update -q
sudo apt-get install -y mininet openvswitch-switch --fix-missing
echo "      OK"
echo ""

# Step 2 — Python dependencies
echo "[2/6] Installing Python dependencies..."
pip3 install scikit-learn numpy pandas scapy xgboost matplotlib \
             joblib pydotplus packaging jsonschema seaborn tqdm \
             ipython wget category_encoders 2>/dev/null
sudo pip3 install numpy scikit-learn  # also needed under sudo for mininet
echo "      OK"
echo ""

# Step 3 — Build dpdk-pipeline binary
echo "[3/6] Building dpdk-pipeline binary..."
if [ ! -f "$PIPELINE_BUILD_DIR/build/pipeline" ]; then
    cp -r /usr/share/dpdk/examples/pipeline "$PIPELINE_BUILD_DIR"
    cd "$PIPELINE_BUILD_DIR"

    # Fix n_pkts_max uninitialized bug in DPDK 20.11 sample app
    if ! grep -q "n_pkts_max = 0" cli.c; then
        sed -i '/params.file_name = tokens\[t0 + 2\];/a\                params.n_pkts_max = 0;' cli.c
    fi

    make
    echo "      OK — binary at $PIPELINE_BUILD_DIR/build/pipeline"
else
    echo "      Already built — skipping"
fi
echo ""

# Step 4 — Planter git setup
echo "[4/6] Configuring Planter git..."
cd "$PLANTER_DIR"
git config core.autocrlf input
echo "      OK"
echo ""

# Step 5 — Fix BMv2 Makefile Python path
echo "[5/6] Applying P4Pi compatibility fixes..."
MAKEFILE="$PLANTER_DIR/src/targets/bmv2/software/utils/Makefile"
if grep -q "python3.12" "$MAKEFILE"; then
    sed -i 's|/usr/local/lib/python3.12/site-packages|/usr/lib/python3/dist-packages|g' "$MAKEFILE"
    echo "      Fixed python3.12 path in BMv2 Makefile"
fi

# Disable t4p4s service that conflicts with port 50051
sudo systemctl stop t4p4s 2>/dev/null || true
sudo systemctl disable t4p4s 2>/dev/null || true
echo "      Disabled t4p4s service (port 50051 conflict)"
echo ""

echo "========================================================"
echo " Setup complete!"
echo ""
echo " To run flow classification (Decision Tree on DPDK):"
echo "   cd ~/Planter && python3 Planter.py"
echo ""
echo " To run anomaly detection (Random Forest on DPDK):"
echo "   cd ~/Planter"
echo "   python3 -c \"import json; c=json.load(open('src/configs/Planter_config.json')); c['model config']['model']='RF'; json.dump(c,open('src/configs/Planter_config.json','w'),indent=4)\""
echo "   PLANTER_FORCE_GENERATE_ENTRIES=1 python3 Planter.py"
echo ""
echo " See examples/ for full documentation."
echo "========================================================"