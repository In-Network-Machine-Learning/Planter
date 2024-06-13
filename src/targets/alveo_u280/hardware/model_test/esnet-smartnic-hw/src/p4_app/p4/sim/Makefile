#
# ESnet smartnic P4 simulation
#

# P4 source file. Override this to pick something else.
# Note that the build target of this Makefile creates a .json
# file as an artifact (needed by the P4 behavior model simulation)
# in the same directory as the .p4 source file, which might be
# somewhere different from the Makefile.
P4_SOURCE = ../p4_app.p4
P4_OBJECT = $(P4_SOURCE:.p4=.json)
# JSON object file as seen from $(P4BM_DIR)
P4_OBJECT_TEST = ../$(P4_OBJECT)

# Directory to use for input and output test vectors..
# We assume that each test case is a subdirectory below the
# sim directory.
P4BM_DIR = test-default

# Directories to use for p4bm simulation
P4BM_DIRS = test-default test-default-w-drops test-fwd-p0 test-pkt-loopback

# Directories to use for system verilog simulation
SVH_DIRS = test-default test-default-w-drops test-fwd-p0

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
P4BM_OUTPUTS = $(P4BM_OUTPUT_META) $(P4BM_OUTPUT_PCAP) $(P4BM_OUTPUT_PCAP_TXT) $(P4BM_LOGFILE_PREFIX)_cli.txt $(P4BM_LOGFILE_PREFIX)_model.txt $(P4BM_OUTPUT_TXT) expected/$(P4BM_OUTPUT_PCAP_TXT)
DIFF_PCAP = diff.pcap

# Send all log info to text files instead of console.

# Where to get executables (particularly if they're not in $PATH)
P4C_VITISNET = p4c-vitisnet
RUN_P4BM_VITISNET = run-p4bm-vitisnet
RUN_P4BM_OPTIONS  = -d
TCPDUMP = tcpdump

# Use a locally-modified version of pcap_diff that can compare
# packet payloads as well as cooked headers.
# Upstream pcap_diff.py is at https://github.com/isginf/pcap-diff
PCAP_DIFF = ./pcap_diff.py

# editcap comes from wireshark
EDITCAP = editcap

# Vitisnet uses C++ models to simulate the interface and functionality
# of extern blocks if needed by a P4 program.
EXTERN_DIR = user_externs
EXTERNS = $(wildcard $(EXTERN_DIR)/*.so)
# Comma-separated list of extern C++ object files as seen from $(P4BM_DIR)
EXTERN_SO_LIST_TEST = $(shell echo $(EXTERNS:%=../%) | tr ' ' ',')

all: build sim

build: $(P4_OBJECT)

extern:
	$(MAKE) -C $(EXTERN_DIR)

sim:
# Make sure that $(P4BM_DIR)/$(P4BM_SCRIPT) exists.  run-p4bm-sdnet
# reacts badly if the script file doesn't exist.
	(cd $(P4BM_DIR) && wc $(P4BM_SCRIPT) > /dev/null)
	(cd $(P4BM_DIR) && $(RUN_P4BM_VITISNET) $(RUN_P4BM_OPTIONS) -l $(P4BM_LOGFILE_PREFIX) -j $(P4_OBJECT_TEST) -s $(P4BM_SCRIPT) )
	(cd $(P4BM_DIR) && $(TCPDUMP) -envXX -r $(P4BM_OUTPUT_PCAP) > $(P4BM_OUTPUT_PCAP_TXT))
	(cd $(P4BM_DIR) && $(TCPDUMP) -envXX -r expected/$(P4BM_OUTPUT_PCAP) > expected/$(P4BM_OUTPUT_PCAP_TXT))


sim-svh: sim
	(echo \`SVTEST\( $(shell echo $(P4BM_DIR) | sed 's/\-/\_/g') \)                   >> $(P4BM_OUTPUT_SVH) )
	(echo run_pkt_test \( \.testdir\( \"$(P4BM_DIR)\" \)\, \.init_timestamp\(1\) \)\; >> $(P4BM_OUTPUT_SVH) )
	(echo \`SVTEST_END                                                                >> $(P4BM_OUTPUT_SVH) )
	(echo                                                                             >> $(P4BM_OUTPUT_SVH) )

test:
	(cd $(P4BM_DIR) && ../$(PCAP_DIFF) -c -d -i expected/$(P4BM_OUTPUT_PCAP) -i $(P4BM_OUTPUT_PCAP) -o $(DIFF_PCAP) | tee $(P4BM_OUTPUT_TXT))
	grep 'Found 0 different packets' $(P4BM_DIR)/$(P4BM_OUTPUT_TXT) > /dev/null

cleansim:
	rm -f $(P4BM_OUTPUT_SVH)
	(cd $(P4BM_DIR) && rm -f $(P4BM_OUTPUTS) $(DIFF_PCAP))

clean: cleansim
	rm -f $(P4_OBJECT)

%.json: %.p4
	$(P4C_VITISNET) $< -o $@

# All
sim-all: build
	for d in $(P4BM_DIRS); do $(MAKE) P4BM_DIR=$$d sim || exit 1; done

sim-all-svh: cleansim build
	for d in $(SVH_DIRS); do $(MAKE) P4BM_DIR=$$d sim-svh || exit 1; done

test-all:
	for d in $(P4BM_TEST_DIRS); do $(MAKE) P4BM_DIR=$$d test || exit 1; done

cleansim-all:
	for d in $(P4BM_DIRS); do $(MAKE) P4BM_DIR=$$d cleansim; done

