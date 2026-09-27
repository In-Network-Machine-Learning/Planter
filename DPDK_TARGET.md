# p4c-dpdk Target for Planter

Documentation for the `p4c-dpdk` target added on the `gsoc-p4c-dpdk` branch.
For general Planter documentation, see the [main README](./README.md).

Google Summer of Code 2026 · Project 3.3 · The P4 Language Consortium
Contributor: Yuzhong (WeiWei) Luo · Mentor: Dr Peng Qian · University of Oxford

---

## Overview

Planter converts trained scikit-learn models into P4 programs and match–action
table entries, then deploys them to a target. Its low-cost options previously
ended at BMv2, which suits functional validation but not sustained traffic. This
branch adds the missing path to `p4c-dpdk`, so the same generated model can run
on DPDK's SWX software pipeline on [P4Pi](https://github.com/p4lang/p4pi).

Three contributions:

1. **A `p4c-dpdk` target adapter** — `src/targets/dpdk/software/`
2. **Fixes to Planter's PSA architecture generator** — `src/architectures/psa/`,
   which had not previously been validated for ML model generation
3. **A P4Pi image build overlay** — `image-build/`, rebuilding the P4Pi image
   with Planter preinstalled

---

## Quick start

Assumes a Raspberry Pi 4 running the
[P4Pi SIGCOMM 2022 image](https://github.com/p4lang/p4pi/releases).

```bash
git clone https://github.com/In-Network-Machine-Learning/Planter.git
cd Planter
chmod +x setup.sh && ./setup.sh      # dependencies + dpdk-pipeline build
python3 Planter.py -m
```

At the prompts:

| Prompt | Value |
|---|---|
| Model | `DT` or `RF` |
| Type | `EB` |
| Dataset | `Iris` |
| Architecture | `psa` |
| Device | `dpdk` |
| Mode | `software` |

The run trains the model, generates PSA P4, compiles it with `p4c-dpdk`, patches
the `.spec`, writes table entry files, launches `dpdk-pipeline`, and reports
accuracy against the scikit-learn baseline.

---

## Results

Iris, 70/30 split, Raspberry Pi 4, DPDK 20.11.5:

| Model | scikit-learn | BMv2 | DPDK |
|---|---|---|---|
| Decision Tree (depth 4) | 95.56% | 95.56% | **95.56%** |
| Random Forest (5 trees, depth 4) | 93.33% | 93.33% | **91.11%** |

Decision Tree matches the BMv2 baseline exactly. The Random Forest gap is a known
coverage bug — see [Known issues](#known-issues).

---

## How the adapter works

`src/targets/dpdk/software/run_model.py` implements five stages:

| Function | Responsibility |
|---|---|
| `compile_p4_dpdk()` | Runs `p4c --target dpdk --arch psa`, locates the generated `.spec` |
| `patch_spec_file()` | Applies DPDK 20.11 workarounds to the compiled `.spec` |
| `generate_entry_files()` | Converts Planter's ternary tables to exact-match entry files (model-aware: DT and RF differ) |
| `generate_cli_script()` | Writes the `dpdk-pipeline` CLI script with the correct table load order |
| `run_dpdk_pipeline()` | Launches the pipeline in `--no-huge` mode and captures output |

`test_model.py` builds the test packets, runs the pipeline, decodes the result
field from the output pcap (including a byte-order correction) and reports
accuracy.

---

## PSA generator fixes

`src/architectures/psa/p4_generator.py` existed but had not been exercised for ML
model generation, and its output did not compile. Eight fixes were required:

1. Missing `struct metadata_t {}` wrapper — metadata fields were emitted at file
   top level
2. Missing `out empty_t` parameters in the ingress deparser
3. Missing `out empty_t` parameters in the egress deparser
4. `empty_t` not defined in this build's `psa.p4` — now emitted explicitly
5. Missing trailing `in empty_t` parameters in the ingress parser
6. Missing trailing `in empty_t` parameters in the egress parser
7. Wrong metadata type in the egress control
   (`psa_egress_parser_input_metadata_t` → `psa_egress_input_metadata_t`)
8. The BMv2 target adapter always invoked the v1model compiler regardless of the
   configured architecture

After these, both `p4c-bm2-psa` and `p4c --target dpdk --arch psa` compile the
generated PSA cleanly. These fixes affect any use of the PSA generator, not only
the DPDK path.

---

## DPDK 20.11 limitations

The P4Pi SIGCOMM 2022 image ships DPDK 20.11.5. Six limitations in its SWX
runtime are not documented upstream; `patch_spec_file()` works around each:

| Limitation | Workaround |
|---|---|
| No wildcard/ternary table backend (`rte_swx_table_wildcard_match` was added in DPDK 21.08) | Expand ternary ranges into exact-match entries using Planter's matching formula `(x & V) == (V & M)` |
| Mask parsing unimplemented in the text entry format — the source contains `/* TBD Set entry->key_mask */` and the mask is never written | Exact-match expansion makes masks unnecessary |
| `lookahead` absent from the SWX instruction set | Remove the lookahead block; the etherType check already gates the path |
| `drop` absent from the SWX instruction set | Replace with `tx` to a sink port |
| Table size must satisfy `n/4 = 2^k` for hash bucket addressing | Compute the size from the actual entry count and round up |
| `n_pkts_max` uninitialised in the `dpdk-pipeline` sample app | Patch `cli.c` to set `n_pkts_max = 0` |

Several of these no longer apply on newer DPDK releases. `--no-huge` is used
throughout, removing the hugepage reservation step that would otherwise need
reapplying after every reboot.

---

## Example applications

| Example | Model | Description |
|---|---|---|
| [`examples/flow_classification/`](examples/flow_classification/) | Decision Tree | Classifying flows by packet header features |
| [`examples/anomaly_detection/`](examples/anomaly_detection/) | Random Forest | Multi-class traffic classification |

Each includes a README written for classroom use.

---

## P4Pi image build

[`image-build/`](image-build/) rebuilds the P4Pi image with Planter, `p4c`, BMv2
and `dpdk-pipeline` preinstalled, so no setup is needed after flashing.

This was necessary because the original P4Pi build depends on OpenSUSE OBS
repositories that no longer exist:

```
$ curl https://api.opensuse.org/public/build/home:p4pi
<status code="unknown_project">Project not found: home:p4pi</status>
```

The overlay replaces those package sources with builds from pinned upstream tags
— p4c v1.2.5.16 and BMv2 1.15.5, with the BMv2 and DPDK backends enabled. See
[`image-build/README.md`](image-build/README.md) for the build procedure and the
cross-build issues encountered.

---

## Known issues

- **Random Forest range coverage.** RF reaches 91.11% against a 93.33% BMv2
  baseline. Exact-match expansion should be lossless, so this indicates the
  expansion is not enumerating every covered value for RF's multi-code ternary
  format. Under investigation.
- **XGBoost.** Compiles and loads its feature tables, but the pipeline crashes at
  runtime on DPDK 20.11. Under investigation.
- **Image boot verification.** The image builds cleanly and passes an in-image
  smoke test, but has not yet been flashed and booted on physical hardware.
- **TAP interfaces.** DPDK creates TAP devices successfully, but the `link` and
  `ethdev` port types in the DPDK 20.11 `dpdk-pipeline` sample app do not accept
  them without additional ethdev initialisation. Testing currently uses pcap
  source/sink ports.

---

## Files added or modified

```
src/targets/dpdk/software/     p4c-dpdk target adapter (new)
src/architectures/psa/         PSA generator (fixed)
src/targets/bmv2/software/     Architecture-aware compiler selection (fixed)
examples/                      Example applications (new)
image-build/                   P4Pi image build overlay (new)
scripts/                       Ternary-to-exact-match conversion utility
setup.sh                       One-command environment setup (new)
```

---

## Upstream

- Python 3.12 compatibility fix:
  [Planter PR #10](https://github.com/In-Network-Machine-Learning/Planter/pull/10)
- PSA generator fixes and the DPDK target: PRs to
  [Planter](https://github.com/In-Network-Machine-Learning/Planter) to follow
- Image build fixes: PR to [P4Pi](https://github.com/p4lang/p4pi) to follow
