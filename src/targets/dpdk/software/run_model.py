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
# Functions: This file is a P4 compiler and runner of the P4 target.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.
#
# Author: Yuzhong (WeiWei) Luo
# Date: 2026-06-24

import os
import sys
import stat
import subprocess as sub
import json
import time
import signal
import platform
import threading
from multiprocessing import *
import getpass
from src.functions.json_encoder import *
from src.functions.add_license import *
from src.functions.extract_log_file_info import *


def file_names(Planter_config):
    work_root = Planter_config['directory config']['work']
    model_test_root = Planter_config['directory config']['work'] + '/src/targets/dpdk/software/model_test/test_environment'
    file_name = Planter_config['model config']['model'] + '_' + Planter_config['target config']['use case'] + '_' + \
                Planter_config['data config']['dataset']
    test_file_name = 'test_switch_model_' + Planter_config['target config']['device'] + '_' + Planter_config['target config']['type']
    return work_root, model_test_root, file_name, test_file_name

def compile_p4_dpdk(p4_file, output_dir):
    """Compile P4 file with p4c-dpdk. Returns (success, spec_path, error)."""
    os.makedirs(output_dir, exist_ok=True)
    cmd = ['p4c', '--target', 'dpdk', '--arch', 'psa', p4_file, '-o', output_dir]
    sub.run(['sudo', 'killall', 'pipeline'], capture_output=True)
    sub.run(['sudo', 'rm', '-rf', '/var/run/dpdk/rte/'], capture_output=True)
    result = sub.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, None, result.stderr
    p4_basename = os.path.splitext(os.path.basename(p4_file))[0]
    spec_path = os.path.join(output_dir, p4_basename + '.spec')
    if not os.path.exists(spec_path):
        return False, None, f"Spec file not found at {spec_path}"
    return True, spec_path, None


def next_valid_size(n_entries):
    """Smallest n where n/4 is a power of 2, n >= n_entries, and n >= 8."""
    buckets = 1
    while buckets * 4 < n_entries:
        buckets *= 2
    return max(buckets * 4, 8)


def patch_spec_file(spec_path, entries_dir):
    """Apply DPDK 20.11 workarounds to the compiled .spec file."""
    with open(spec_path, 'r') as f:
        spec = f.read()

    # Fix 1: wildcard -> exact (DPDK 20.11 has no wildcard table backend)
    spec = spec.replace(' wildcard', ' exact')

    # Fix 2: remove lookahead block (instruction doesn't exist in DPDK 20.11)
    import re
    lookahead_pattern = re.compile(
        r'(SWITCHINGRESSPARSER_CHECK_PLANTER_VERSION\s*:\s*)lookahead.*?'
        r'jmp SWITCHINGRESSPARSER_ACCEPT\n',
        re.DOTALL
    )
    spec = lookahead_pattern.sub(
        r'\1jmp SWITCHINGRESSPARSER_PARSE_PLANTER\n',
        spec
    )

    # Fix 3: drop -> tx (drop instruction doesn't exist in DPDK 20.11)
    spec = spec.replace(
        'LABEL_DROP :\tdrop',
        'LABEL_DROP :\ttx m.psa_ingress_output_metadata_egress_port'
    )
    spec = spec.replace(
        'LABEL_DROP :    drop',
        'LABEL_DROP :    tx m.psa_ingress_output_metadata_egress_port'
    )

    # Fix 4: correct table sizes to match actual entry counts
    # (must satisfy n/4 = power of 2 for DPDK's hash bucket addressing)
    _cfg = json.load(open('src/configs/Planter_config.json'))
    _model = _cfg.get('model config', {}).get('model', 'DT')
    table_entry_files = {f'lookup_feature{n}': f'lookup_feature{n}_entries.txt' for n in range(4)}
    if _model in ('RF', 'XGB'):
        _n_trees = _cfg.get('model config', {}).get('number of trees', 5)
        for i in range(_n_trees):
            table_entry_files[f'lookup_leaf_id{i}'] = f'lookup_leaf_id{i}_entries.txt'
    table_entry_files['decision'] = 'decision_entries.txt'
    lines = spec.splitlines()
    for table_name, entry_file in table_entry_files.items():
        entry_path = os.path.join(entries_dir, entry_file)
        if not os.path.exists(entry_path):
            continue

        with open(entry_path) as ef:
            n_entries = sum(1 for line in ef if line.strip())

        # Keep one extra slot for default/action-state overhead to avoid commit failures
        # when table entry count equals nominal size.
        correct_size = next_valid_size(n_entries + 1)

        in_target_table = False
        brace_depth = 0
        for i, line in enumerate(lines):
            stripped = line.strip()

            if not in_target_table:
                if stripped.startswith(f'table {table_name} '):
                    in_target_table = True
                    brace_depth += line.count('{') - line.count('}')
                continue

            # While inside target table, replace its size line.
            if stripped.startswith('size '):
                indent = line[:len(line) - len(line.lstrip())]
                lines[i] = f"{indent}size {hex(correct_size)}"

            brace_depth += line.count('{') - line.count('}')
            if brace_depth <= 0:
                in_target_table = False
                brace_depth = 0

    spec = '\n'.join(lines) + '\n'

    # Fix 5: Correct RF leaf table key extraction in spec.
    # p4c-dpdk generates wrong shr/and amounts for bit-slice table keys.
    # For tree 0 the spec copies the full packed code_fN with no masking;
    # for trees 1-4 the shr offsets are computed incorrectly.
    # We patch to extract exactly the right bits per (tree, feature) pair,
    # matching the per-tree codes stored in Exact_Table['tree N'].
    # NOTE: the apply-block in the spec uses a single tab (\t) for indentation.
    if _model in ('RF', 'XGB') and 'width of code' in _cfg.get('p4 config', {}):
        _woc       = _cfg['p4 config']['width of code']   # [tree][feature]
        _n_trees_w = len(_woc)
        _n_feats_w = len(_woc[0]) if _n_trees_w > 0 else 4

        # --- tree 0: plain mov — add masking via Ingress_tmp (same pattern as trees 1-N) ---
        for _f in range(_n_feats_w):
            _mask    = (1 << int(_woc[0][_f])) - 1
            _key_reg = 'Ingress_key' if _f == 0 else f'Ingress_key_{_f - 1}'
            _old = f'\tmov m.{_key_reg} m.local_metadata_code_f{_f}\n'
            _new = (f'\tmov m.Ingress_tmp m.local_metadata_code_f{_f}\n'
                    f'\tand m.Ingress_tmp 0x{_mask:x}\n'
                    f'\tmov m.{_key_reg} m.Ingress_tmp\n')
            spec = spec.replace(_old, _new, 1)

        # --- trees 1-N: fix shr offset and AND mask in each 4-line key-prep block ---
        # Pattern: mov tmp code_fF; shr tmp WRONG; and tmp WRONG_MASK; mov key_Y tmp
        # key_Y register index (1-based from key_0) encodes (tree, feature):
        #   reg_idx = key_number + 1  →  tree = reg_idx // n_features,  feat = reg_idx % n_features
        def _fix_leaf_shr(m):
            tmp_reg  = m.group(1)
            feat_num = int(m.group(2))
            key_full = m.group(3)
            key_n_s  = m.group(4)          # numeric suffix of key reg, or None
            if key_n_s is None:
                return m.group(0)          # unnumbered key = tree 0, already handled
            key_n    = int(key_n_s)
            reg_idx  = key_n + 1           # Ingress_key_0 → reg 1
            tree_n   = reg_idx // _n_feats_w
            feat_f   = reg_idx % _n_feats_w
            if tree_n < 1:
                return m.group(0)
            c_shr  = int(sum(_woc[T][feat_f] for T in range(tree_n)))
            c_mask = (1 << int(_woc[tree_n][feat_f])) - 1
            return (f'\tmov m.{tmp_reg} m.local_metadata_code_f{feat_num}\n'
                    f'\tshr m.{tmp_reg} 0x{c_shr:x}\n'
                    f'\tand m.{tmp_reg} 0x{c_mask:x}\n'
                    f'\tmov m.{key_full} m.{tmp_reg}')

        _leaf_key_pat = re.compile(
            r'\tmov m\.(Ingress_tmp_?\d*) m\.local_metadata_code_f(\d+)\n'
            r'\tshr m\.\1 0x[0-9a-f]+\n'
            r'\tand m\.\1 0x[0-9a-f]+\n'
            r'\tmov m\.(Ingress_key(?:_(\d+))?) m\.\1'
        )
        spec = _leaf_key_pat.sub(_fix_leaf_shr, spec)

    # Fix 6: Align 32-bit scratch registers to 4-byte boundaries.
    # A trailing bit<8> field (e.g. local_metadata_flag) can leave the
    # Ingress_tmp / Ingress_key registers at offset%4 == 2, causing a
    # SIGBUS on ARM when the DPDK executor performs aligned 32-bit loads.
    # Insert bit<8> padding fields (never bit<16> — unsupported by DPDK 20.11)
    # before the first Ingress_tmp to reach the next 4-byte boundary.
    _first_tmp = spec.find('\n\tbit<32> Ingress_tmp\n')
    if _first_tmp != -1:
        # Compute byte offset of Ingress_tmp in the metadata struct
        _ms = spec.find('struct metadata_t {')
        _fragment = spec[_ms:_first_tmp]
        _offset = 0
        for _fl in _fragment.split('\n'):
            _fm = re.match(r'\s+bit<(\d+)>', _fl)
            if _fm:
                _offset += (int(_fm.group(1)) + 7) // 8
        _pad = (-_offset) % 4            # bytes needed to reach next 4-byte boundary
        if _pad > 0:
            # Use bit<8> fields only — DPDK 20.11 doesn't support bit<16>
            _pad_decl = ''.join(f'\n\tbit<8> _planter_align_pad_{i}' for i in range(_pad))
            spec = spec[:_first_tmp] + _pad_decl + spec[_first_tmp:]

    with open(spec_path, 'w') as f:
        f.write(spec)
    print(f"Patched spec written to {spec_path}")

def generate_entry_files_rf(work_root, output_dir):
    """Expand RF table JSON files into per-table entry files for dpdk-pipeline."""
    os.makedirs(output_dir, exist_ok=True)

    config_path = os.path.join(work_root, 'src', 'configs', 'Planter_config.json')
    with open(config_path) as f:
        planter_config = json.load(f)
    # width_of_code[tree][feature] — bit width allocated for each tree's code
    # in each feature's packed metadata field (stored by the model generator)
    width_of_code = planter_config['p4 config']['width of code']
    n_trees = len(width_of_code)

    ternary_json = os.path.join(work_root, 'Tables', 'Ternary_Table.json')
    exact_json   = os.path.join(work_root, 'Tables', 'Exact_Table.json')
    with open(ternary_json) as f:
        ternary_table = json.load(f)
    with open(exact_json) as f:
        exact_table = json.load(f)

    def covered_values(value, mask):
        target = value & mask
        return [x for x in range(256) if (x & value) == target]

    def pack_codes(codes_list, feature_n):
        """Pack per-tree codes into the single combined metadata value for feature_n.

        Each tree's code occupies a contiguous bit slice of the combined field,
        starting at the cumulative shift determined by the widths of all
        preceding trees for this feature (matching the P4 key-slice layout).
        """
        packed = 0
        shift = 0
        for t in range(n_trees):
            packed |= (int(codes_list[t]) << shift)
            shift += int(width_of_code[t][feature_n])
        return packed

    # Feature lookup tables (ternary) — write the packed combined code
    for n in range(4):
        lines = []
        seen = {}
        for entry in ternary_table[f'feature {n}'].values():
            value, mask, code_list = entry[0], entry[1], entry[2]
            code = pack_codes(code_list, n)
            for x in covered_values(value, mask):
                if x not in seen:
                    seen[x] = code
                    lines.append(f"match {x} action extract_feature{n} tree H({code})")
        out_path = os.path.join(output_dir, f'lookup_feature{n}_entries.txt')
        with open(out_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        print(f"  Wrote {len(lines)} entries -> {out_path}")

    # Leaf lookup tables (exact) — one per tree
    for n in range(n_trees):
        lines = []
        for entry in exact_table[f'tree {n}'].values():
            f0   = entry['f0 code']
            f1   = entry['f1 code']
            f2   = entry['f2 code']
            f3   = entry['f3 code']
            leaf = entry['leaf']
            lines.append(f"match {f0} {f1} {f2} {f3} action read_prob{n} prob H(0) vote H({int(leaf)})")
        out_path = os.path.join(output_dir, f'lookup_leaf_id{n}_entries.txt')
        with open(out_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        print(f"  Wrote {len(lines)} entries -> {out_path}")

    # Decision table — dynamic so it works for any number of trees
    lines = []
    for entry in exact_table['decision'].values():
        votes = ' '.join(str(entry[f't{i} vote']) for i in range(n_trees))
        cls   = entry['class']
        lines.append(f"match {votes} action read_lable label N({int(cls)})")
    out_path = os.path.join(output_dir, 'decision_entries.txt')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  Wrote {len(lines)} entries -> {out_path}")


def generate_entry_files(work_root, output_dir):
    """Expand table JSON files into per-table entry files for dpdk-pipeline."""
    config_path = os.path.join(work_root, 'src', 'configs', 'Planter_config.json')
    with open(config_path) as f:
        planter_config = json.load(f)
    model = planter_config.get('model config', {}).get('model', 'DT')

    if model in ('RF', 'XGB'):
        generate_entry_files_rf(work_root, output_dir)
        return

    # DT path
    os.makedirs(output_dir, exist_ok=True)
    ternary_json = os.path.join(work_root, 'Tables', 'Ternary_Table.json')
    with open(ternary_json) as f:
        table = json.load(f)

    def covered_values(value, mask):
        target = value & mask
        return [x for x in range(256) if (x & value) == target]

    # Feature lookup tables
    for n in range(4):
        lines = []
        seen = {}
        for entry in table[f'feature {n}'].values():
            value, mask, code = entry[0], entry[1], entry[2]
            for x in covered_values(value, mask):
                if x not in seen:
                    seen[x] = code
                    lines.append(f"match {x} action extract_feature{n} tree H({int(code)})")
        out_path = os.path.join(output_dir, f'lookup_feature{n}_entries.txt')
        with open(out_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        print(f"  Wrote {len(lines)} entries -> {out_path}")

    # Decision table
    lines = []
    for entry in table['code to vote'].values():
        f0, f1, f2, f3 = entry['f0 code'], entry['f1 code'], entry['f2 code'], entry['f3 code']
        leaf = entry['leaf']
        lines.append(f"match {f0} {f1} {f2} {f3} action read_lable label N({int(leaf)})")
    out_path = os.path.join(output_dir, 'decision_entries.txt')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  Wrote {len(lines)} entries -> {out_path}")


def generate_cli_script(cli_path, spec_path, entries_dir,
                         input_pcap, output_pcap, model='DT', n_trees=5):
    """Write the dpdk-pipeline CLI script."""
    tables = [f'lookup_feature{n}' for n in range(4)]
    if model in ('RF', 'XGB'):
        tables += [f'lookup_leaf_id{i}' for i in range(n_trees)]
    tables.append('decision')
    with open(cli_path, 'w') as f:
        f.write("mempool MEMPOOL0 buffer 2304 pool 32K cache 256 cpu 0\n")
        f.write("pipeline PIPELINE0 create 0\n")
        f.write(f"pipeline PIPELINE0 port in 0 source MEMPOOL0 {input_pcap}\n")
        f.write(f"pipeline PIPELINE0 port out 0 sink {output_pcap}\n")
        f.write(f"pipeline PIPELINE0 build {spec_path}\n")
        for table in tables:
            entry_file = os.path.join(entries_dir, f'{table}_entries.txt')
            f.write(f"pipeline PIPELINE0 table {table} update "
                    f"{entry_file} none none\n")
        f.write("thread 1 pipeline PIPELINE0 enable\n")
    print(f"CLI script written to {cli_path}")

def run_dpdk_pipeline(cli_path, pipeline_binary, log_path, output_pcap=None, timeout=30):
    """
    Launch dpdk-pipeline, wait for it to process packets, capture log.
    Returns (success, log_output)
    """
    cmd = ['sudo', pipeline_binary, '--no-huge', '-m', '256', '-c', '0x3', '--', '-s', cli_path]
    output_pcap = None

    def has_cli_table_errors(log_text):
        return ('Error in file "' in log_text) or ('Invalid entry in file' in log_text)

    try:
        with open(cli_path, 'r') as cli_file:
            for line in cli_file:
                if line.startswith('pipeline PIPELINE0 port out 0 sink '):
                    output_pcap = line.strip().split()[-1]
                    break
    except OSError:
        pass

    if output_pcap and os.path.exists(output_pcap):
        try:
            os.remove(output_pcap)
        except OSError:
            pass

    try:
        result = sub.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        log_output = result.stdout + result.stderr
        with open(log_path, 'w') as f:
            f.write(log_output)
        if result.returncode != 0 or has_cli_table_errors(log_output):
            if result.returncode != 0:
                log_output = f'[DPDK exit code: {result.returncode}]\n' + log_output
            return False, log_output
        return True, log_output
    except sub.TimeoutExpired as e:
        # Normal — pipeline runs forever until killed, timeout = success
        log_output = (e.stdout or b'').decode('utf-8', errors='replace') + \
             (e.stderr or b'').decode('utf-8', errors='replace')
        with open(log_path, 'w') as f:
            f.write(log_output)
        if has_cli_table_errors(log_output):
            return False, log_output
        return True, log_output
    except Exception as e:
        return False, str(e)

def add_make_run_model(fname, config):
    work_root, model_test_root, file_name, test_file_name = file_names(config)
    
    spec_dir    = os.path.join(model_test_root, 'spec')
    entries_dir = os.path.join(model_test_root, 'entries')
    manual_entries_dir = os.path.join(work_root, 'scripts', 'dpdk_entries')
    input_pcap  = os.path.join(model_test_root, 'test_input.pcap')
    output_pcap = os.path.join(model_test_root, 'test_output.pcap')
    cli_path    = os.path.join(model_test_root, 'run.cli')
    log_path    = os.path.join(model_test_root, 'run.log')
    pipeline_bin = config.get('dpdk config', {}).get('pipeline_bin', os.path.expanduser('~/dpdk_pipeline_build/build/pipeline'))

    p4_file = os.path.join(work_root, 'P4', file_name + '.p4')

    _model_name  = config['model config']['model']
    _n_trees_req = config['model config'].get('number of trees', 5)
    required_entry_files = [f'lookup_feature{n}_entries.txt' for n in range(4)]
    if _model_name in ('RF', 'XGB'):
        required_entry_files += [f'lookup_leaf_id{i}_entries.txt' for i in range(_n_trees_req)]
    required_entry_files.append('decision_entries.txt')
    manual_entries_available = all(
        os.path.exists(os.path.join(manual_entries_dir, name))
        for name in required_entry_files
    )
    force_generate_entries = os.environ.get('PLANTER_FORCE_GENERATE_ENTRIES', '0') == '1'

    # Step 1 — compile
    print("Compiling P4 with p4c-dpdk...")
    success, spec_path, err = compile_p4_dpdk(p4_file, spec_dir)
    if not success:
        print(f"Compile failed:\n{err}")
        return

    # Step 2 — choose entry source FIRST (patch_spec_file needs them for size calculation)
    if manual_entries_available and not force_generate_entries:
        entries_source_dir = manual_entries_dir
        print(f"Using pre-validated entry files from {entries_source_dir}")
    else:
        entries_source_dir = entries_dir
        if force_generate_entries:
            print("Force-generating table entry files (PLANTER_FORCE_GENERATE_ENTRIES=1)...")
        else:
            print("Generating table entry files...")
        generate_entry_files(work_root, entries_source_dir)

    # Step 3 — patch spec (now entry files exist for size counting)
    print("Patching spec file...")
    patch_spec_file(spec_path, entries_source_dir)

    # Step 4 — generate CLI script
    print("Generating CLI script...")
    model = config['model config']['model']
    n_trees = config['model config'].get('number of trees', 5)
    generate_cli_script(cli_path, spec_path, entries_source_dir, input_pcap, output_pcap,
                        model=model, n_trees=n_trees)

    # Store paths in config for test_model.py to use
    config['dpdk config'] = {
        'cli_path':     cli_path,
        'output_pcap':  output_pcap,
        'log_path':     log_path,
        'pipeline_bin': pipeline_bin,
        'entries_dir':  entries_source_dir,
    }
    json.dump(config, open('src/configs/Planter_config.json', 'w'), indent=4)
    print("run_model setup complete — ready to run pipeline")


def term(sig_num, addition):
    print('Killing pid %s with group id %s' % (os.getpid(), os.getpgrp()))
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)


def main(if_using_subprocess):
    if platform.system() != 'Linux':
        print('DPDK target requires Linux.')
        exit()

    config_file = 'src/configs/Planter_config.json'
    Planter_config = json.load(open(config_file, 'r'))
    Planter_config['test config']['sudo password'] = getpass.getpass(
        "- Please input your password for 'sudo' command: ") or 'raspberry'
    json.dump(Planter_config, open(config_file, 'w'), indent=4, cls=NpEncoder)

    add_make_run_model(config_file, Planter_config)

    signal.signal(signal.SIGTERM, term)
    print('current pid is %s' % os.getpid())
    processes = []
    if_using_subprocess = False
    return processes, if_using_subprocess