#include <stdio.h>
#include <argp.h> /* argp_parse */
#include <stdbool.h> /* bool */
#include <string.h>  /* strcmp */
#include <stdlib.h>  /* getenv */

#include "smartnic.h"		/* smartnic_* */
#include "arguments_common.h"	/* arguments_global, cmd_* */

const char *argp_program_version = "sn-cli 2.0";
const char *argp_program_bug_address = "ESnet SmartNIC Developers <smartnic@es.net>";

/* Program documentation. */
static char doc_global[] = "Tool for interacting with an esnet-smartnic based on a Xilinx U280 card.";

/* A description of the arguments we accept. */
static char args_doc_global[] = "(cmac | dev | probe | qdma | sw)";

static struct argp_option argp_options_global[] = {
					    { "slotaddr", 's',
					      "BDF", 0,
					      "PCIe BDF address of the FPGA card.  Value can also be loaded from SN_CLI_SLOTADDR env var.",
					      0,
					    },
					    { "verbose", 'v',
					      0, 0,
					      "Produce verbose output",
					      0,
					    },
					    // Manually provide --help here rather than globally to allow subcommands
					    // to implement their own help functions
					    { "help", '?',
					      0, 0,
					      "Give this help list",
					      0,
					    },
					    { 0, 0,
					      0, 0,
					      0,
					      0,
					    },
};

static error_t parse_opt_global (int key, char *arg, struct argp_state *state)
{
  struct arguments_global *arguments = state->input;

  switch (key) {
  case 's':
    arguments->pcieaddr = arg;
    break;
  case 'v':
    arguments->verbose = true;
    break;
  case '?':
    argp_state_help(state, state->out_stream, ARGP_HELP_STD_HELP);
    break;
  case ARGP_KEY_ARG:
    if (strcmp(arg, "cmac") == 0) {
      cmd_cmac(state);
    } else if (strcmp(arg, "qdma") == 0) {
      cmd_qdma(state);
    } else if (strcmp(arg, "probe") == 0) {
      cmd_probe(state);
    } else if (strcmp(arg, "dev") == 0) {
      cmd_dev(state);
    } else if (strcmp(arg, "sw") == 0) {
      cmd_sw(state);
    } else {
      argp_error(state, "%s is not a valid command", arg);
    }
    break;
  case ARGP_KEY_END:
    if (state->arg_num < 1) {
      // Not enough arguments
      argp_usage (state);
    }
    break;
  default:
    return ARGP_ERR_UNKNOWN;
  }

  return 0;
}


int main(int argc, char *argv[])
{
  struct arguments_global arguments = {
    .verbose = false,
  };

  struct argp argp_global = {
    .options  = argp_options_global,
    .parser   = parse_opt_global,
    .args_doc = args_doc_global,
    .doc      = doc_global,
  };

  // Prepopulate the PCIE address from the environment variable (if set)
  arguments.pcieaddr = getenv("SN_CLI_SLOTADDR");

  argp_parse (&argp_global, argc, argv, ARGP_IN_ORDER | ARGP_NO_HELP, 0, &arguments);

  return 0;
}
