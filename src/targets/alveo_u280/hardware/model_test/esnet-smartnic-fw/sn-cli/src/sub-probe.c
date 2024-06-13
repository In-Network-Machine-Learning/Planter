#include <stdio.h>
#include <argp.h> /* argp_parse */
#include <stdbool.h> /* bool */
#include <string.h>  /* strcmp */
#include <stdlib.h>  /* malloc */
#include <inttypes.h>		/* strtoumax */

#include "smartnic.h"		/* smartnic_* */
#include "array_size.h"		/* ARRAY_SIZE */
#include "memory-barriers.h"	/* barrier */
#include "arguments_common.h"	/* arguments_global, cmd_* */

static char doc_probe[] =
  "\n"
  "This subcommand is used to interact with the smartnic interface probes"
  "\v"
  "--"
  ;

static char args_doc_probe[] = "(stats)";

static struct argp_option argp_options_probe[] = {
  { "format", 'f',
    "FORMAT", 0,
    "Format of output (default: table)",
    0,
  },
  { "nolatch", 'n',
    0, 0,
    "Do not latch/clear internal counters",
    0,
  },
  { "probe", 'p',
    "PROBE", 0,
    "smartnic interface probe to act on (default is all)",
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

#define PROBE_SELECT_FROM_CMAC_0 (1 << 0)
#define PROBE_SELECT_TO_CMAC_0   (1 << 1)
#define PROBE_SELECT_CMAC_0      (PROBE_SELECT_FROM_CMAC_0 | PROBE_SELECT_TO_CMAC_0)
#define PROBE_SELECT_FROM_CMAC_1 (1 << 2)
#define PROBE_SELECT_TO_CMAC_1   (1 << 3)
#define PROBE_SELECT_CMAC_1      (PROBE_SELECT_FROM_CMAC_1 | PROBE_SELECT_TO_CMAC_1)
#define PROBE_SELECT_CMAC        (PROBE_SELECT_CMAC_0 | PROBE_SELECT_CMAC_1)
#define PROBE_SELECT_FROM_HOST_0 (1 << 4)
#define PROBE_SELECT_TO_HOST_0   (1 << 5)
#define PROBE_SELECT_HOST_0      (PROBE_SELECT_FROM_HOST_0 | PROBE_SELECT_TO_HOST_0)
#define PROBE_SELECT_FROM_HOST_1 (1 << 6)
#define PROBE_SELECT_TO_HOST_1   (1 << 7)
#define PROBE_SELECT_HOST_1      (PROBE_SELECT_FROM_HOST_1 | PROBE_SELECT_TO_HOST_1)
#define PROBE_SELECT_HOST        (PROBE_SELECT_HOST_0 | PROBE_SELECT_HOST_1)
#define PROBE_SELECT_CORE_TO_APP_0 (1 << 8)
#define PROBE_SELECT_APP_0_TO_CORE (1 << 9)
#define PROBE_SELECT_APP_0         (PROBE_SELECT_CORE_TO_APP_0 | PROBE_SELECT_APP_0_TO_CORE)
#define PROBE_SELECT_CORE_TO_APP_1 (1 << 10)
#define PROBE_SELECT_APP_1_TO_CORE (1 << 11)
#define PROBE_SELECT_APP_1         (PROBE_SELECT_CORE_TO_APP_1 | PROBE_SELECT_APP_1_TO_CORE)
#define PROBE_SELECT_BYPASS        (1 << 12)
#define PROBE_SELECT_DROP          (1 << 13)
#define PROBE_SELECT_CORE_TO_APP   (PROBE_SELECT_CORE_TO_APP_0 | PROBE_SELECT_CORE_TO_APP_1 | PROBE_SELECT_BYPASS | PROBE_SELECT_DROP)
#define PROBE_SELECT_APP_TO_CORE   (PROBE_SELECT_APP_0_TO_CORE | PROBE_SELECT_APP_1_TO_CORE)
#define PROBE_SELECT_APP           (PROBE_SELECT_CORE_TO_APP | PROBE_SELECT_APP_TO_CORE)
#define PROBE_SELECT_ALL (\
			  PROBE_SELECT_CMAC_0 | \
			  PROBE_SELECT_CMAC_1 | \
			  PROBE_SELECT_HOST_0 | \
			  PROBE_SELECT_HOST_1 | \
			  PROBE_SELECT_APP)

struct arguments_probe {
  struct arguments_global* global;
  enum output_format output_format;
  char *command;
  uint32_t probes;
};

static error_t parse_opt_probe (int key, char *arg, struct argp_state *state)
{
  struct arguments_probe *arguments = state->input;

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
    if (!strcmp(arg, "all")) {
      arguments->probes |= PROBE_SELECT_ALL;
    } else if (!strcmp(arg, "cmac")) {
      arguments->probes |= PROBE_SELECT_CMAC;
    } else if (!strcmp(arg, "cmac0")) {
      arguments->probes |= PROBE_SELECT_CMAC_0;
    } else if (!strcmp(arg, "cmac1")) {
      arguments->probes |= PROBE_SELECT_CMAC_1;
    } else if (!strcmp(arg, "host")) {
      arguments->probes |= PROBE_SELECT_HOST;
    } else if (!strcmp(arg, "host0")) {
      arguments->probes |= PROBE_SELECT_HOST_0;
    } else if (!strcmp(arg, "host1")) {
      arguments->probes |= PROBE_SELECT_HOST_1;
    } else if (!strcmp(arg, "app")) {
      arguments->probes |= PROBE_SELECT_APP;
    } else if (!strcmp(arg, "app0")) {
      arguments->probes |= PROBE_SELECT_APP_0;
    } else if (!strcmp(arg, "app1")) {
      arguments->probes |= PROBE_SELECT_APP_1;
    } else if (!strcmp(arg, "bypass")) {
      arguments->probes |= PROBE_SELECT_BYPASS;
    } else if (!strcmp(arg, "drop")) {
      arguments->probes |= PROBE_SELECT_DROP;
    } else if (!strcmp(arg, "app-to-core")) {
      arguments->probes |= PROBE_SELECT_APP_TO_CORE;
    } else if (!strcmp(arg, "core-to-app")) {
      arguments->probes |= PROBE_SELECT_CORE_TO_APP;
    } else {
      // Unknown probe
      argp_error(state, "%s is not a valid probe or probe group", arg);
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

static void print_probe_stats(volatile struct axi4s_probe_block * probe, const char * suffix, bool clear)
{
  uint64_t packet_count;
  uint64_t byte_count;

  if (smartnic_probe_read_counters(probe, &packet_count, &byte_count, clear)) {
    printf("\tPackets: %20lu  Bytes: %20lu  %s\n", packet_count, byte_count, suffix);
  } else {
    printf("\tPackets: %20s  Bytes: %20s  %s\n", "? READ FAIL ?", "? READ FAIL ?", suffix);
  }
  return;
}

void cmd_probe(struct argp_state *state)
{
  struct arguments_probe arguments = {0,};
  int  argc   = state->argc - state->next +1;
  char **argv = &state->argv[state->next - 1];
  char *argv0 = argv[0];

  arguments.global = state->input;

  struct argp argp_probe = {
    .options  = argp_options_probe,
    .parser   = parse_opt_probe,
    .args_doc = args_doc_probe,
    .doc      = doc_probe,
  };

  // Temporarily override argv[0] to make error messages show the correct prefix
  argv[0] = malloc(strlen(state->name) + strlen(" probe") + 1);
  if (!argv[0]) {
    argp_failure(state, 1, ENOMEM, 0);
  }
  sprintf(argv[0], "%s probe", state->name);

  // Invoke the subcommand parser
  argp_parse (&argp_probe, argc, argv, ARGP_IN_ORDER, &argc, &arguments);

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

  if (arguments.probes == 0) {
    // When no probes are specified, the default is to act on all probes
    arguments.probes = PROBE_SELECT_ALL;
  }

  if (!strcmp(arguments.command, "stats")) {
    // Ingress Probes

    printf("Ingress toward p4 application\n");
    printf("-----------------------------\n");

    if (arguments.probes & PROBE_SELECT_FROM_CMAC_0) {
      printf("From CMAC 0\n");
      print_probe_stats(&bar2->probe_from_cmac_0, "ok", false);
      print_probe_stats(&bar2->drops_err_from_cmac_0, "error/drop", false);
      print_probe_stats(&bar2->drops_ovfl_from_cmac_0, "ovfl/drop", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_FROM_CMAC_1) {
      printf("From CMAC 1\n");
      print_probe_stats(&bar2->probe_from_cmac_1, "ok", false);
      print_probe_stats(&bar2->drops_err_from_cmac_1, "error/drop", false);
      print_probe_stats(&bar2->drops_ovfl_from_cmac_1, "ovfl/drop", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_FROM_HOST_0) {
      printf("From HOST PF 0 (h2c)\n");
      print_probe_stats(&bar2->probe_from_host_0, "ok", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_FROM_HOST_1) {
      printf("From HOST PF 1 (h2c)\n");
      print_probe_stats(&bar2->probe_from_host_1, "ok", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_CORE_TO_APP_0) {
      printf("Smartnic Platform to P4 App 0 Input\n");
      print_probe_stats(&bar2->probe_core_to_app0, "ok", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_CORE_TO_APP_1) {
      printf("Smartnic Platform to P4 App 1 Input\n");
      print_probe_stats(&bar2->probe_core_to_app1, "ok", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_BYPASS) {
      printf("Smartnic Platform to Bypass\n");
      print_probe_stats(&bar2->probe_to_bypass, "ok", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_DROP) {
      printf("Smartnic Platform to Ingress Blackhole\n");
      print_probe_stats(&bar2->drops_from_igr_sw, "ok/drop", false);
      printf("\n");
    }

    // Egress Probes

    printf("Egress from p4 application\n");
    printf("--------------------------\n");

    if (arguments.probes & PROBE_SELECT_APP_0_TO_CORE) {
      printf("P4 App 0 Output to Smartnic Platform\n");
      print_probe_stats(&bar2->probe_app0_to_core, "ok", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_APP_1_TO_CORE) {
      printf("P4 App 1 Output to Smartnic Platform\n");
      print_probe_stats(&bar2->probe_app1_to_core, "ok", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_TO_HOST_0) {
      printf("To HOST PF 0 (c2h)\n");
      print_probe_stats(&bar2->probe_to_host_0, "ok", false);
      print_probe_stats(&bar2->drops_ovfl_to_host_0, "ovfl/drop", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_TO_HOST_1) {
      printf("To HOST PF 1 (c2h)\n");
      print_probe_stats(&bar2->probe_to_host_1, "ok", false);
      print_probe_stats(&bar2->drops_ovfl_to_host_1, "ovfl/drop", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_TO_CMAC_0) {
      printf("To CMAC 0\n");
      print_probe_stats(&bar2->probe_to_cmac_0, "ok", false);
      print_probe_stats(&bar2->drops_ovfl_to_cmac_0, "ovfl/drop", false);
      printf("\n");
    }

    if (arguments.probes & PROBE_SELECT_TO_CMAC_1) {
      printf("To CMAC 1\n");
      print_probe_stats(&bar2->probe_to_cmac_1, "ok", false);
      print_probe_stats(&bar2->drops_ovfl_to_cmac_1, "ovfl/drop", false);
      printf("\n");
    }

  } else {
    fprintf(stderr, "ERROR: %s is not a valid command\n", arguments.command);
  }

  return;
}

