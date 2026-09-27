# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF THE LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is a P4 tester of the P4 target (DPDK software).
#            Please refer to ./Docs/Planter_User_Document.pdf for further information.
#
# Author: Yuzhong (WeiWei) Luo
# Date: 2026-07-04

import os
import sys
import json
import struct
import numpy as np
from multiprocessing import Process
from scapy.all import *
from sklearn.metrics import classification_report, accuracy_score
from src.functions.json_encoder import *
from src.functions.add_license import *
from src.targets.dpdk.software.run_model import (
    file_names, run_dpdk_pipeline
)


def build_test_packets(test_X, num_features, input_pcap):
    """
    Build all test samples into a single input pcap file.
    Returns the Planter scapy class so we can decode output packets later.
    """
    class Planter(Packet):
        name = 'Planter'
        fields_desc = (
            [StrFixedLenField('P', 'P', length=1),
             StrFixedLenField('Four', '4', length=1),
             XByteField('version', 0x01),
             XByteField('type', 0x01)] +
            [IntField(f'feature{f}', 0) for f in range(num_features)] +
            [IntField('result', 0xDEADBABE)]
        )
    bind_layers(Ether, Planter, type=0x1234)

    pkts = []
    for i in range(len(test_X)):
        kwargs = {f'feature{f}': int(test_X[i][f]) for f in range(num_features)}
        kwargs['result'] = 404
        pkt = Ether(dst='00:04:00:00:00:00', type=0x1234) / Planter(**kwargs)
        pkts.append(pkt)

    wrpcap(input_pcap, pkts)
    print(f"Built {len(pkts)} test packets -> {input_pcap}")
    return Planter


def read_results(output_pcap, n_expected, PlantedClass):
    """
    Read the first n_expected packets from the output pcap,
    extracting the result field from each one.
    Returns a list of integer predictions.
    """
    results = []
    with PcapReader(output_pcap) as reader:
        for pkt in reader:
            if PlantedClass in pkt:
                raw = int(pkt[PlantedClass].result)
                # Some targets emit decision labels in network order; convert
                # only clearly byte-shifted 32-bit class IDs (e.g., 0x02000000).
                if raw > 0xFF and (raw & 0x00FFFFFF) == 0:
                    corrected = struct.unpack('>I', struct.pack('<I', raw))[0]
                    results.append(corrected)
                else:
                    results.append(raw)
            else:
                results.append(-1)
            if len(results) >= n_expected:
                break
    return results


def main(sklearn_test_y, test_X, test_y, processes, if_using_subprocess):
    # Reload config
    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    work_root, model_test_root, file_name, test_file_name = file_names(Planter_config)

    # Save test data for logging
    Test_Data = {
        'sklearn_test_y': sklearn_test_y,
        'test_X': test_X.values.tolist() if hasattr(test_X, 'values') else test_X,
        'test_y': test_y
    }
    json.dump(Test_Data,
              open(work_root + '/src/temp/Test_Data.json', 'w'),
              indent=4, cls=NpEncoder)

    num_features = Planter_config['data config']['number of features']
    dpdk         = Planter_config.get('dpdk config', {})

    input_pcap   = os.path.join(model_test_root, 'test_input.pcap')
    output_pcap  = dpdk.get('output_pcap',  os.path.join(model_test_root, 'test_output.pcap'))
    log_path     = dpdk.get('log_path',     os.path.join(model_test_root, 'run.log'))
    cli_path     = dpdk.get('cli_path',     os.path.join(model_test_root, 'run.cli'))
    pipeline_bin = dpdk.get('pipeline_bin', os.path.expanduser('~/dpdk_pipeline_build/build/pipeline'))

    n = len(Test_Data['test_X'])

    # Step 1 — build all test packets into one pcap
    print("Building test packets...")
    PlantedClass = build_test_packets(Test_Data['test_X'], num_features, input_pcap)

    # Step 2 — run the DPDK pipeline (reads input pcap, writes output pcap)
    print("Running DPDK pipeline...")
    success, log = run_dpdk_pipeline(cli_path, pipeline_bin, log_path, output_pcap=output_pcap, timeout=90)
    if not success:
        print(f"Pipeline failed:\n{log}")
        return processes, if_using_subprocess

    # Step 3 — read classifications out of the output pcap
    print("Reading output pcap...")
    switch_test_y = read_results(output_pcap, n, PlantedClass)

    if len(switch_test_y) < n:
        print(f"WARNING: only got {len(switch_test_y)} results, expected {n}")

    # Step 4 — print per-sample results and final accuracy report
    print("\n==============================================================================================")
    print("=        DPDK Pipeline Classification Results                                               =")
    print("==============================================================================================")
    print("Test the switch model — result should match the python-based test above\n")

    for i, (pred, true) in enumerate(zip(switch_test_y, test_y)):
        correct_so_far = sum(p == t for p, t in zip(switch_test_y[:i+1], test_y[:i+1]))
        acc = correct_so_far / (i + 1)
        same = sum(p == s for p, s in zip(switch_test_y[:i+1], sklearn_test_y[:i+1])) / (i + 1)
        print(f"Switch model {i+1}th prediction: {pred}, test_y: {true}, "
              f"with acc: {acc:.3f}, with acc to sklearn: {same:.4f}")

    report = classification_report(
        test_y[:len(switch_test_y)],
        switch_test_y,
        digits=4
    )
    print('\n', report)
    print("======================================= Test Finished ========================================")

    # Append classification report to the run log for GitHub upload
    with open(log_path, 'a') as f:
        f.write('\n\n=== Classification Report ===\n')
        f.write(report)

    if not if_using_subprocess:
        if_using_subprocess = True

    # Clean up large output pcap to prevent disk full
    import subprocess
    subprocess.run(['sudo', 'rm', '-f', output_pcap], capture_output=True)

    return processes, if_using_subprocess


if __name__ == "__main__":
    # Quick standalone test
    from src.load_data.Iris_dataset import load_data
    train_X, train_y, test_X, test_y, used_features = load_data(4, 'Data')
    main(test_y.tolist(), test_X, test_y.tolist(), [], False)