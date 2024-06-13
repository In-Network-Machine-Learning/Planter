# ===========================================================================
# ESnet smartnic P4 simulation
# ===========================================================================

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------
# P4 source file. 
# Note that the build target creates a .json file (used by the P4 behavioral simulator)
# in the same directory as the P4 source file, which may be different from the Makefile
# directory.
P4_SOURCE = ../p4_hbm.p4
P4_OBJECT = $(P4_SOURCE:.p4=.json)

# JSON object file as seen from $(P4BM_DIR)
P4_OBJECT_TEST = ../$(P4_OBJECT)

# Default testcase directory.  Assumes each test case is a subdir below the sim dir.
P4BM_DIR = test-v4-accept

# Testcase directory list to use for p4bm simulation
P4BM_DIRS = test-v4-accept \
            test-v4-drop \
            test-v6-accept \
            test-v6-drop

# Testcase directory list to use for system verilog simulation
SVH_DIRS = $(P4BM_DIRS)

# Directories to use for test (against expected "golden" known-good
# output traces. By default is the same as $(P4BM_DIRS) but can be
# overridden to exclude certain (or all) directories for scenarios
# where we don't yet have expected output traces.
P4BM_TEST_DIRS = $(P4BM_DIRS)

# Files within each test directory, as seen from within $(P4BM_DIR)
# Note that $(P4BM_OUTPUT_PCAP) and $(P4BM_OUTPUT_META) are
# implicitly named in $(P4BM_SCRIPT).
P4BM_SCRIPT = runsim.txt
P4BM_LOGFILE_PREFIX = $(P4BM_SCRIPT)
P4BM_OUTPUT_PCAP = packets_out.pcap
P4BM_OUTPUT_PCAP_TXT = packets_out.pcap.txt
P4BM_OUTPUT_META = packets_out.meta
P4BM_OUTPUT_TXT = sim-out.txt
P4BM_OUTPUT_SVH = run_pkt_test_incl.svh
P4BM_OUTPUTS = $(P4BM_OUTPUT_META) $(P4BM_OUTPUT_PCAP) $(P4BM_OUTPUT_PCAP_TXT) $(P4BM_LOGFILE_PREFIX)_cli.txt $(P4BM_LOGFILE_PREFIX)_model.txt $(P4BM_OUTPUT_TXT)

# Executable pathnames (particularly if they're not in $PATH)
P4C_VITISNET      = p4c-vitisnet
RUN_P4BM_VITISNET = run-p4bm-vitisnet

# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------
test-all:
	for d in $(P4BM_TEST_DIRS); do $(MAKE) P4BM_DIR=$$d test || exit 1; done

sim-all: build
	for d in $(P4BM_DIRS); do $(MAKE) P4BM_DIR=$$d sim || exit 1; done

sim-all-svh: cleansim build
	for d in $(SVH_DIRS); do $(MAKE) P4BM_DIR=$$d sim-svh || exit 1; done

sim: build
# Make sure that $(P4BM_DIR)/$(P4BM_SCRIPT) exists (avoids issues if script is missing).
	(cd $(P4BM_DIR) && wc $(P4BM_SCRIPT) > /dev/null)
	(cd $(P4BM_DIR) && $(RUN_P4BM_VITISNET) -l $(P4BM_LOGFILE_PREFIX) \
                                             -j $(P4_OBJECT_TEST) -s $(P4BM_SCRIPT) )

test: sim
	cd $(P4BM_DIR) && ./check.sh

build: $(P4_OBJECT)

sim-svh: sim
	(echo \`SVTEST\( $(shell echo $(P4BM_DIR) | sed 's/\-/\_/g') \)                   >> $(P4BM_OUTPUT_SVH) )
	(echo run_pkt_test \( \.testdir\( \"$(P4BM_DIR)\" \)\, \.init_timestamp\(1\) \)\; >> $(P4BM_OUTPUT_SVH) )
	(echo \`SVTEST_END                                                                >> $(P4BM_OUTPUT_SVH) )
	(echo                                                                             >> $(P4BM_OUTPUT_SVH) )

cleansim-all:
	for d in $(P4BM_DIRS); do $(MAKE) P4BM_DIR=$$d cleansim; done

cleansim:
	rm -f $(P4BM_OUTPUT_SVH)
	cd $(P4BM_DIR) && rm -f $(P4BM_OUTPUTS)

clean: cleansim-all
	rm -f $(P4_OBJECT)

.PHONY: test-all sim-all sim-all-svh sim test build sim-svh cleansim-all cleansim clean

%.json: %.p4
	$(P4C_VITISNET) $< -o $@


