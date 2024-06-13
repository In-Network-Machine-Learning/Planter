#include <stdio.h>
#include <argp.h> /* argp_parse */
#include <stdbool.h> /* bool */
#include <string.h>  /* strcmp */
#include <stdlib.h>  /* malloc */
#include <inttypes.h>		/* strtoumax */

#include "smartnic.h"		/* smartnic_* */
#include "array_size.h"		/* ARRAY_SIZE */
#include "arguments_common.h"	/* arguments_global, cmd_* */

static char doc_qdma[] =
  "\n"
  "This subcommand is used to interact with the Xilinx QDMA blocks within the smartnic"
  "\v"
  "--"
  ;

static char args_doc_qdma[] = "(setqs | status | stats)";

static struct argp_option argp_options_qdma[] = {
  { "format", 'f',
    "FORMAT", 0,
    "Format of output (default: table)",
    0,
  },
  { "physfunc", 'p',
    "PF", 0,
    "PCIe physical function (PF) number to act on",
    0,
  },
  { 0, 0,
    0, 0,
    0,
    0,
  },
};

enum output_format {
  OUTPUT_FORMAT_TABLE = 0,
  OUTPUT_FORMAT_MAX, // Add entries above this line
};

#define PF_SELECT_PF0 (1 << 0)
#define PF_SELECT_PF1 (1 << 1)
#define PF_SELECT_ALL (PF_SELECT_PF0 | PF_SELECT_PF1)
#define PF_SELECT_NUM_PFS 2

// This is limited by the indexes used in the open-nic-shell RSS distribution function lookup table
// The QDMA block itself likely supports a higher number of queues per PF
#define QDMA_MAX_QUEUES_PER_PF 128

struct arguments_qdma {
  struct arguments_global* global;
  enum output_format output_format;
  char *command;
  uint32_t pcie_pfs;
  uint32_t needed_args;
  uintmax_t additional_args[PF_SELECT_NUM_PFS];
};

static error_t parse_opt_qdma (int key, char *arg, struct argp_state *state)
{
  struct arguments_qdma *arguments = state->input;

  switch(key) {
  case 'f':
    if (!strcmp(arg, "table")) {
      arguments->output_format = OUTPUT_FORMAT_TABLE;
    } else {
      // Unknown config file format
      argp_usage (state);
    }
    break;
  case 'p':
    {
      uintmax_t v;
      char *end;

      // Convert the arg to an integer, taking care to pre-clear errno
      errno = 0;
      v = strtoumax(arg, &end, 10);

      // Check for all the ways the conversion can fail
      if (*end != '\0') {
	// trailing garbage means it didn't convert properly
	argp_error(state, "%s can't be converted to a pcie physical function number", arg);
      } else if (v == UINTMAX_MAX && errno == ERANGE) {
	// value is out of range
	argp_error(state, "%s is out of range for pcie physical function conversion", arg);
      } else if (v >= PF_SELECT_NUM_PFS) {
	// value is not a valid port number
	argp_error(state, "%s is not a valid pcie physical function number", arg);
      } else {
	// found a valid port number, set it in the physical function select bitmask
	arguments->pcie_pfs |= (1 << v);
      }
    }
    break;
  case ARGP_KEY_ARG:
    if (state->arg_num == 0) {
      if (!strcmp(arg, "setqs")) {
	// Make sure we get a queue setting for all possible PFs
	arguments->needed_args = PF_SELECT_NUM_PFS;
      } else if (!strcmp(arg, "status")) {
	arguments->needed_args = 0;
      } else if (!strcmp(arg, "stats")) {
	arguments->needed_args = 0;
      } else {
	// Unrecognized command
	argp_error(state, "%s is not a valid command", arg);
      }
      arguments->command = arg;
    } else {
      if (state->arg_num > arguments->needed_args) {
	// Too many arguments
	argp_usage (state);
      } else if (state->arg_num > ARRAY_SIZE(arguments->additional_args)) {
	// We're expecting more arguments than we have room for in our state variable, oops
	argp_error(state, "BUG: internal arg storage can't hold %u required arguments\n", arguments->needed_args);
      } else {
	uintmax_t v;
	char *end;

	errno = 0;
	v = strtoumax(arg, &end, 10);
	
	// Check for all the ways the conversion can fail
	if (*end != '\0') {
	  // trailing garbage means it didn't convert properly
	  argp_error(state, "%s can't be converted to a number of queues", arg);
	} else if (v == UINTMAX_MAX && errno == ERANGE) {
	  // value is out of range
	  argp_error(state, "%s is out of range for number of queues conversion", arg);
	} else if (v > QDMA_MAX_QUEUES_PER_PF) {
	  // value is too big to be used as the number of queues for a PF
	  argp_error(state, "%s is greater than the max allowed (%u) queues per PF", arg, QDMA_MAX_QUEUES_PER_PF);
	} else {
	  // found a valid port number, set it in the physical function select bitmask
	  arguments->additional_args[state->arg_num - 1] = v;
	}
      }
    }
    break;
  case ARGP_KEY_END:
    if (state->arg_num < (arguments->needed_args + 1)) {
      // Not enough arguments
      argp_usage (state);
    }
    break;
  case ARGP_KEY_SUCCESS:
  case ARGP_KEY_ERROR:
    // Always claim to have consumed all options and arguments to prevent the parent from reparsing
    // options after the subcommand
    state->next = state->argc;
    break;
  default:
    return ARGP_ERR_UNKNOWN;
  }

  return 0;
}

static void print_qdma_status(volatile struct qdma_function_block * qdma)
{
  union qdma_function_qconf qconf;

  qconf._v = qdma->qconf._v;
  printf("\tQueue Config:\n");
  printf("\t\tbase:  %u\n", qconf.qbase);
  printf("\t\tnumq:  %u\n", qconf.numq);
  printf("\t\trange: ");
  if (qconf.numq > 0) {
    printf("%u - %u\n",
	   qconf.qbase,
	   qconf.qbase + qconf.numq - 1);
  } else {
    printf("empty\n");
  }

  printf("\n");
  
  printf("\tRSS Entropy (hex) -> Relative QID (decimal) Map\n");
  for (unsigned int row=0; row < 8; row++) {
    if (row == 0) {
      // Print the column headings before the first row
      printf("\t\t\t");
      for (unsigned int col=0; col < 16; col++) {
	printf("    %x ", col);
      }
      printf("\n");

      printf("\t\t\t");
      for (unsigned int col=0; col < 16; col++) {
	printf("    - ");
      }
      printf("\n");
    }
    // Print a row of values
    printf("\t\t0x%02x\t", row * 16);
    for (unsigned int col=0; col < 16; col++) {
      // Print the colums for this row
      uint32_t qid = qdma->indir_table[row * 16 + col];
      printf("%5u ", qid & 0x0000FFFF);
    }
    printf("\n");
  }
  printf("\n");
  return;
}

static void print_qdma_stats(volatile struct cmac_adapter_block * adapter)
{
  printf("\tRx (c2h) (box322 -> box250)\n");
  printf("\t  %15s: %lu\n", "packets    ok", ((uint64_t)adapter->rx_packets_hi << 32) | adapter->rx_packets_lo);
  printf("\t  %15s: %lu\n", "bytes      ok", ((uint64_t)adapter->rx_bytes_hi << 32) | adapter->rx_bytes_lo);
  printf("\t  %15s: %lu\n", "packets   err", ((uint64_t)adapter->rx_err_packets_hi << 32) | adapter->rx_err_packets_lo);
  printf("\t  %15s: %lu\n", "bytes     err", ((uint64_t)adapter->rx_err_bytes_hi << 32) | adapter->rx_err_bytes_lo);
  printf("\t  %15s: %lu\n", "packets  drop", ((uint64_t)adapter->rx_drop_packets_hi << 32) | adapter->rx_drop_packets_lo);
  printf("\t  %15s: %lu\n", "bytes    drop", ((uint64_t)adapter->rx_drop_bytes_lo << 32) | adapter->rx_drop_bytes_lo);
  printf("\n");

  printf("\tTx (h2c) (box250 -> box322)\n");
  printf("\t  %15s: %lu\n", "packets    ok", ((uint64_t)adapter->tx_packets_hi << 32) | adapter->tx_packets_lo);
  printf("\t  %15s: %lu\n", "bytes      ok", ((uint64_t)adapter->tx_bytes_hi << 32) | adapter->tx_bytes_lo);
  printf("\t  %15s: %lu\n", "packets  drop", ((uint64_t)adapter->tx_drop_packets_hi << 32) | adapter->tx_drop_packets_lo);
  printf("\t  %15s: %lu\n", "bytes    drop", ((uint64_t)adapter->tx_drop_bytes_hi << 32) | adapter->tx_drop_bytes_lo);
  printf("\n");
  return;
}

static void qdma_func_set_queue_map(volatile struct qdma_function_block * qdma, uint16_t qbase, uint16_t numq)
{
  union qdma_function_qconf qconf = {
    .numq = numq,
    .qbase = qbase,
  };

  // Set up RSS hash indirect table to spread hash values across configured queues
  for (unsigned int i = 0; i < ARRAY_SIZE(qdma->indir_table); i++) {
    if (numq > 0) {
      qdma->indir_table[i] = i % numq;
    } else {
      qdma->indir_table[i] = 0;
    }
  }

  // Configure the queues available to the user logic
  qdma->qconf._v = qconf._v;

  return;
}

void cmd_qdma(struct argp_state *state)
{
  struct arguments_qdma arguments = {0,};
  int  argc   = state->argc - state->next +1;
  char **argv = &state->argv[state->next - 1];
  char *argv0 = argv[0];

  arguments.global = state->input;

  struct argp argp_qdma = {
    .options  = argp_options_qdma,
    .parser   = parse_opt_qdma,
    .args_doc = args_doc_qdma,
    .doc      = doc_qdma,
  };

  // Temporarily override argv[0] to make error messages show the correct prefix
  argv[0] = malloc(strlen(state->name) + strlen(" qdma") + 1);
  if (!argv[0]) {
    argp_failure(state, 1, ENOMEM, 0);
  }
  sprintf(argv[0], "%s qdma", state->name);

  // Invoke the subcommand parser
  argp_parse (&argp_qdma, argc, argv, ARGP_IN_ORDER, &argc, &arguments);

  // Restore the previous argv[0]
  free(argv[0]);
  argv[0] = argv0;

  // Always claim to have consumed all options in the subcommand to prevent the parent from reparsing
  // any options that occur after the subcommand
  state->next += argc - 1;

  // Make sure we've been given a PCIe address to work with
  if (arguments.global->pcieaddr == NULL) {
    fprintf(stderr, "ERROR: PCIe address is required but has not been provided\n");
    return;
  }

  // Map the FPGA register space
  volatile struct esnet_smartnic_bar2 * bar2;
  bar2 = smartnic_map_bar2_by_pciaddr(arguments.global->pcieaddr);
  if (bar2 == NULL) {
    fprintf(stderr, "ERROR: failed to mmap FPGA register space for device %s\n", arguments.global->pcieaddr);
    return;
  }

  if (arguments.pcie_pfs == 0) {
    // When no PFs are specified, the default is to act on all PFs
    arguments.pcie_pfs = PF_SELECT_ALL;
  }

  if (!strcmp(arguments.command, "setqs")) {
    uint32_t qbase = 0;

    printf("Configuring PF0 (qbase %u, numq %lu)\n",
	   qbase,
	   arguments.additional_args[0]);
    qdma_func_set_queue_map(&bar2->qdma_func0, qbase, arguments.additional_args[0]);
    qbase += arguments.additional_args[0];
    
    printf("Configuring PF1 (qbase %u, numq %lu)\n",
	   qbase,
	   arguments.additional_args[1]);
    qdma_func_set_queue_map(&bar2->qdma_func1, qbase, arguments.additional_args[1]);
    qbase += arguments.additional_args[1];

  } else if (!strcmp(arguments.command, "status")) {
    if (arguments.pcie_pfs & PF_SELECT_PF0) {
      printf("PF0\n");
      print_qdma_status(&bar2->qdma_func0);
      printf("\n");
    }

    if (arguments.pcie_pfs & PF_SELECT_PF1) {
      printf("PF1\n");
      print_qdma_status(&bar2->qdma_func1);
      printf("\n");
    }

  } else if (!strcmp(arguments.command, "stats")) {
    if (arguments.pcie_pfs & PF_SELECT_PF0) {
      printf("PF0\n");
      print_qdma_stats(&bar2->cmac_adapter0);
      printf("\n");
    }

    if (arguments.pcie_pfs & PF_SELECT_PF1) {
      printf("PF1\n");
      print_qdma_stats(&bar2->cmac_adapter1);
      printf("\n");
    }

  } else {
    fprintf(stderr, "ERROR: %s is not a valid command\n", arguments.command);
  }

  return;
}

