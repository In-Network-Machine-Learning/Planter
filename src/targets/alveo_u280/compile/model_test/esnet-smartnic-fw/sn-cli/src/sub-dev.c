#include <stdio.h>
#include <argp.h> /* argp_parse */
#include <stdbool.h> /* bool */
#include <string.h>  /* strcmp */
#include <stdlib.h>  /* malloc */
#include <inttypes.h>		/* strtoumax */

#include "smartnic.h"		/* smartnic_* */
#include "sysmon.h"		/* sysmon_* */
#include "syscfg_block.h"	/* syscfg_* */
#include "arguments_common.h"	/* arguments_global, cmd_* */

static char doc_dev[] =
  "\n"
  "This subcommand is used to inspect the device level status of the smartnic"
  "\v"
  "--"
  ;

static char args_doc_dev[] = "(version | temp)";

static struct argp_option argp_options_dev[] = {
  { "format", 'f',
    "FORMAT", 0,
    "Format of output (default: table)",
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

struct arguments_dev {
  struct arguments_global* global;
  enum output_format output_format;
  char *command;
};

static error_t parse_opt_dev (int key, char *arg, struct argp_state *state)
{
  struct arguments_dev *arguments = state->input;

  switch(key) {
  case 'f':
    if (!strcmp(arg, "table")) {
      arguments->output_format = OUTPUT_FORMAT_TABLE;
    } else {
      // Unknown config file format
      argp_usage (state);
    }
    break;
  case ARGP_KEY_ARG:
    if (state->arg_num >= 1) {
      // Too many arguments
      argp_usage (state);
    }
    arguments->command = arg;
    break;
  case ARGP_KEY_END:
    if (state->arg_num < 1) {
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

void cmd_dev(struct argp_state *state)
{
  struct arguments_dev arguments = {0,};
  int  argc   = state->argc - state->next +1;
  char **argv = &state->argv[state->next - 1];
  char *argv0 = argv[0];

  arguments.global = state->input;

  struct argp argp_dev = {
    .options  = argp_options_dev,
    .parser   = parse_opt_dev,
    .args_doc = args_doc_dev,
    .doc      = doc_dev,
  };

  // Temporarily override argv[0] to make error messages show the correct prefix
  argv[0] = malloc(strlen(state->name) + strlen(" dev") + 1);
  if (!argv[0]) {
    argp_failure(state, 1, ENOMEM, 0);
  }
  sprintf(argv[0], "%s dev", state->name);

  // Invoke the subcommand parser
  argp_parse (&argp_dev, argc, argv, ARGP_IN_ORDER, &argc, &arguments);

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

  if (!strcmp(arguments.command, "version")) {
    printf("Device Version Info\n");
    printf("\tDNA:           0x%08x%08x%08x\n",
	    bar2->syscfg.dna[2],
	    bar2->syscfg.dna[1],
	    bar2->syscfg.dna[0]);
    printf("\tUSR_ACCESS:    0x%08x (%u)\n", bar2->syscfg.usr_access, bar2->syscfg.usr_access);
    printf("\tBUILD_STATUS:  0x%08x\n", bar2->syscfg.build_status);
  } else if (!strcmp(arguments.command, "temp")) {
    printf("Temperature Monitors\n");
    printf("\tFPGA SLR0:   %7.3f (deg C)\n", sysmon_get_temp(&bar2->sysmon0));
  } else {
    fprintf(stderr, "ERROR: %s is not a valid command\n", arguments.command);
  }

  return;
}

