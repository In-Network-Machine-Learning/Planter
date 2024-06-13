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

static char doc_sw[] =
  "\n"
  "This subcommand is used to interact with the smartnic ingress/egress/bypass switch settings"
  "\v"
  "--"
  ;

static char args_doc_sw[] = "(status|in-port-rename|in-port-connect|bypass-connect|app0-port-redirect|app1-port-redirect|out-fifo-fc-thresh)";

static struct argp_option argp_options_sw[] = {
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

enum switch_map_slot_id {
  SW_MAP_SLOT_MIN     = 0,
  SW_MAP_SLOT_CMAC0   = SW_MAP_SLOT_MIN,
  SW_MAP_SLOT_CMAC1   = 1,
  SW_MAP_SLOT_HOST0   = 2,
  SW_MAP_SLOT_HOST1   = 3,
  SW_MAP_SLOT_NUM_ENTRIES
};

enum switch_map_port_id {
  SW_MAP_PORT_MIN     = 0,
  SW_MAP_PORT_CMAC0   = SW_MAP_PORT_MIN,
  SW_MAP_PORT_CMAC1   = 1,
  SW_MAP_PORT_HOST0   = 2,
  SW_MAP_PORT_HOST1   = 3,
  SW_MAP_PORT_APP0    = 4,
  SW_MAP_PORT_APP1    = 5,
  SW_MAP_PORT_BYPASS  = 6,
  SW_MAP_PORT_DROP    = 7,
  SW_MAP_PORT_DEFAULT = 8,
  SW_MAP_PORT_NUM_ENTRIES
};

struct switch_map {
  enum switch_map_slot_id a;
  enum switch_map_port_id z;
};

struct arguments_sw {
  struct arguments_global* global;
  enum output_format output_format;
  char *command;
  struct switch_map map[SW_MAP_PORT_NUM_ENTRIES];
  uint8_t map_num_valid;
};

static bool sw_map_slot_id_from_name(const char *name, enum switch_map_slot_id *id)
{
  if (id == NULL) {
    return false;
  }
  if (name == NULL) {
    return false;
  }

  if (!strcmp(name, "cmac0")) {
    *id = SW_MAP_SLOT_CMAC0;
  } else if (!strcmp(name, "cmac1")) {
    *id = SW_MAP_SLOT_CMAC1;
  } else if (!strcmp(name, "host0")) {
    *id = SW_MAP_SLOT_HOST0;
  } else if (!strcmp(name, "host1")) {
    *id = SW_MAP_SLOT_HOST1;
  } else {
    return false;
  }

  return true;
}

static bool sw_map_port_id_from_name(const char *name, enum switch_map_port_id *id)
{
  if (id == NULL) {
    return false;
  }
  if (name == NULL) {
    return false;
  }

  if (!strcmp(name, "cmac0")) {
    *id = SW_MAP_PORT_CMAC0;
  } else if (!strcmp(name, "cmac1")) {
    *id = SW_MAP_PORT_CMAC1;
  } else if (!strcmp(name, "host0")) {
    *id = SW_MAP_PORT_HOST0;
  } else if (!strcmp(name, "host1")) {
    *id = SW_MAP_PORT_HOST1;
  } else if (!strcmp(name, "app0")) {
    *id = SW_MAP_PORT_APP0;
  } else if (!strcmp(name, "app1")) {
    *id = SW_MAP_PORT_APP1;
  } else if (!strcmp(name, "bypass")) {
    *id = SW_MAP_PORT_BYPASS;
  } else if (!strcmp(name, "drop")) {
    *id = SW_MAP_PORT_DROP;
  } else if (!strcmp(name, "default")) {
    *id = SW_MAP_PORT_DEFAULT;
  } else {
    return false;
  }

  return true;
}

static error_t parse_opt_sw (int key, char *arg, struct argp_state *state)
{
  struct arguments_sw *arguments = state->input;

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
    if (state->arg_num == 0) {
      // First non option argument is the command
      arguments->command = arg;
    } else {
      // Following non-option arguments are pairs of ports to adjust, add them to the map
      // Format of these arguments is <a-port>:<z-port>
      char *az_pair = strdup(arg);
      char *az_pair_orig = az_pair; /* keep around to free the strdup'd string later */
      char **cursor = &az_pair;

      char *a_port_name = strsep(cursor, ":");
      if (a_port_name == NULL) {
	argp_error(state, "%s is missing an a-port", arg);
	break;
      }
      enum switch_map_slot_id a_port;
      if (!sw_map_slot_id_from_name(a_port_name, &a_port)) {
	argp_error(state, "%s is not a valid slot name", a_port_name);
	break;
      }

      char *z_port_name = *cursor;
      if (z_port_name == NULL) {
	argp_error(state, "%s is missing a z-port", arg);
	break;
      }
      enum switch_map_port_id z_port;
      if (!sw_map_port_id_from_name(z_port_name, &z_port)) {
	argp_error(state, "%s is not a valid port name", z_port_name);
	break;
      }

      if (arguments->map_num_valid >= SW_MAP_PORT_NUM_ENTRIES) {
	// map argument list is already full, no room for this one
	argp_error(state, "too many port map arguments");
	break;
      }
      // Add the map argument to the list
      arguments->map[arguments->map_num_valid].a = a_port;
      arguments->map[arguments->map_num_valid].z = z_port;
      arguments->map_num_valid++;

      free(az_pair_orig);
    }
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

static const char * switch_map_slot_id_to_name(enum switch_map_slot_id slot)
{
  switch (slot) {
  case SW_MAP_SLOT_CMAC0: return "CMAC0";
  case SW_MAP_SLOT_CMAC1: return "CMAC1";
  case SW_MAP_SLOT_HOST0: return "HOST0";
  case SW_MAP_SLOT_HOST1: return "HOST1";
  default: return "????";
  }
}

static const char * switch_map_port_id_to_name(enum switch_map_port_id port)
{
  switch (port) {
  case SW_MAP_PORT_CMAC0:   return "CMAC0";
  case SW_MAP_PORT_CMAC1:   return "CMAC1";
  case SW_MAP_PORT_HOST0:   return "HOST0";
  case SW_MAP_PORT_HOST1:   return "HOST1";
  case SW_MAP_PORT_APP0:    return "APP0";
  case SW_MAP_PORT_APP1:    return "APP1";
  case SW_MAP_PORT_BYPASS:  return "BYPASS";
  case SW_MAP_PORT_DROP:    return "DROP";
  case SW_MAP_PORT_DEFAULT: return "DEFAULT";
  default: return "????";
  }
}

static bool switch_map_port_id_to_igr_sw_tid (enum switch_map_port_id port, union smartnic_322mhz_igr_sw_tid * tid)
{
  switch (port) {
  case SW_MAP_PORT_CMAC0:
    tid->_v = SMARTNIC_322MHZ_IGR_SW_TID_VALUE_CMAC_0;
    return true;
  case SW_MAP_PORT_CMAC1:
    tid->_v = SMARTNIC_322MHZ_IGR_SW_TID_VALUE_CMAC_1;
    return true;
  case SW_MAP_PORT_HOST0:
    tid->_v = SMARTNIC_322MHZ_IGR_SW_TID_VALUE_HOST_0;
    return true;
  case SW_MAP_PORT_HOST1:
    tid->_v = SMARTNIC_322MHZ_IGR_SW_TID_VALUE_HOST_1;
    return true;
  default:
    // Invalid port for this table
    return false;
  }
}

static const char * igr_sw_tid_to_name(union smartnic_322mhz_igr_sw_tid tid)
{
  switch (tid.value) {
  case SMARTNIC_322MHZ_IGR_SW_TID_VALUE_CMAC_0: return "CMAC0";
  case SMARTNIC_322MHZ_IGR_SW_TID_VALUE_CMAC_1: return "CMAC1";
  case SMARTNIC_322MHZ_IGR_SW_TID_VALUE_HOST_0: return "HOST0";
  case SMARTNIC_322MHZ_IGR_SW_TID_VALUE_HOST_1: return "HOST1";
  default:
    return "????";
  }
}

static bool switch_map_port_id_to_igr_sw_tdest (enum switch_map_port_id port, union smartnic_322mhz_igr_sw_tdest * tdest)
{
  switch (port) {
  case SW_MAP_PORT_APP0:
    tdest->_v = SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_APP_0;
    return true;
  case SW_MAP_PORT_APP1:
    tdest->_v = SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_APP_1;
    return true;
  case SW_MAP_PORT_BYPASS:
    tdest->_v = SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_APP_BYPASS;
    return true;
  case SW_MAP_PORT_DROP:
    tdest->_v = SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_DROP;
    return true;
  default:
    // Invalid port for this table
    return false;
  }
}

static const char * igr_sw_tdest_to_name(union smartnic_322mhz_igr_sw_tdest tdest)
{
  switch (tdest.value) {
  case SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_APP_0: return "APP0";
  case SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_APP_1: return "APP1";
  case SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_APP_BYPASS: return "BYPASS";
  case SMARTNIC_322MHZ_IGR_SW_TDEST_VALUE_DROP: return "DROP";
  default:
    return "????";
  }
}

static bool switch_map_port_id_to_bypass_tdest (enum switch_map_port_id port, union smartnic_322mhz_bypass_tdest * tdest)
{
  switch (port) {
  case SW_MAP_PORT_CMAC0:
    tdest->_v = SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_CMAC_0;
    return true;
  case SW_MAP_PORT_CMAC1:
    tdest->_v = SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_CMAC_1;
    return true;
  case SW_MAP_PORT_HOST0:
    tdest->_v = SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_HOST_0;
    return true;
  case SW_MAP_PORT_HOST1:
    tdest->_v = SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_HOST_1;
    return true;
  default:
    // Invalid port for this table
    return false;
  }
}

static const char * bypass_tdest_to_name(union smartnic_322mhz_bypass_tdest tdest)
{
  switch (tdest.value) {
  case SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_CMAC_0: return "CMAC0";
  case SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_CMAC_1: return "CMAC1";
  case SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_HOST_0: return "HOST0";
  case SMARTNIC_322MHZ_BYPASS_TDEST_VALUE_HOST_1: return "HOST1";
  default:
    return "????";
  }
}

static bool switch_map_port_id_to_app_0_tdest_remap (enum switch_map_port_id port, union smartnic_322mhz_app_0_tdest_remap * tdest)
{
  switch (port) {
  case SW_MAP_PORT_CMAC0:
    tdest->_v = SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_CMAC_0;
    return true;
  case SW_MAP_PORT_CMAC1:
    tdest->_v = SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_CMAC_1;
    return true;
  case SW_MAP_PORT_HOST0:
    tdest->_v = SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_HOST_0;
    return true;
  case SW_MAP_PORT_HOST1:
    tdest->_v = SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_HOST_1;
    return true;
  default:
    // Invalid port for this table
    return false;
  }
}

static const char * app_0_tdest_to_name(union smartnic_322mhz_app_0_tdest_remap tdest)
{
  switch (tdest.value) {
  case SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_CMAC_0: return "CMAC0";
  case SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_CMAC_1: return "CMAC1";
  case SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_HOST_0: return "HOST0";
  case SMARTNIC_322MHZ_APP_0_TDEST_REMAP_VALUE_HOST_1: return "HOST1";
  default:
    return "????";
  }
}

static bool switch_map_port_id_to_app_1_tdest_remap (enum switch_map_port_id port, union smartnic_322mhz_app_1_tdest_remap * tdest)
{
  switch (port) {
  case SW_MAP_PORT_CMAC0:
    tdest->_v = SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_CMAC_0;
    return true;
  case SW_MAP_PORT_CMAC1:
    tdest->_v = SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_CMAC_1;
    return true;
  case SW_MAP_PORT_HOST0:
    tdest->_v = SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_HOST_0;
    return true;
  case SW_MAP_PORT_HOST1:
    tdest->_v = SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_HOST_1;
    return true;
  default:
    // Invalid port for this table
    return false;
  }
}

static const char * app_1_tdest_to_name(union smartnic_322mhz_app_1_tdest_remap tdest)
{
  switch (tdest.value) {
  case SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_CMAC_0: return "CMAC0";
  case SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_CMAC_1: return "CMAC1";
  case SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_HOST_0: return "HOST0";
  case SMARTNIC_322MHZ_APP_1_TDEST_REMAP_VALUE_HOST_1: return "HOST1";
  default:
    return "????";
  }
}

static void print_switch_status(volatile struct esnet_smartnic_bar2 * bar2)
{
  // Ingress Switch Input Port Renaming
  printf ("Ingress Switch Input Port Remap\n");
  for (enum switch_map_slot_id slot = SW_MAP_SLOT_MIN; slot < SW_MAP_SLOT_NUM_ENTRIES; slot++) {
    union smartnic_322mhz_igr_sw_tid tid;
    tid._v = bar2->smartnic_322mhz_regs.igr_sw_tid[slot]._v;

    printf ("\t[%u] %s\t%s\n", slot, switch_map_slot_id_to_name(slot), igr_sw_tid_to_name(tid));
  }
  printf("\n");

  // Ingress Switch Logical Port Connection to Application
  printf ("Ingress Switch Logical Port Connection\n");
  printf ("\tslot Logical\tApp Port\n");
  for (enum switch_map_slot_id slot = SW_MAP_SLOT_MIN; slot < SW_MAP_SLOT_NUM_ENTRIES; slot++) {
    union smartnic_322mhz_igr_sw_tdest tdest;
    tdest._v = bar2->smartnic_322mhz_regs.igr_sw_tdest[slot]._v;

    printf ("\t[%u]  %s\t%s\n", slot, switch_map_slot_id_to_name(slot), igr_sw_tdest_to_name(tdest));
  }
  printf("\n");

  // Bypass Logical Input Port Connection to Logical Output Port
  printf ("Bypass Port Connection\n");
  printf ("\tslot IN\tOUT\n");
  for (enum switch_map_slot_id slot = SW_MAP_SLOT_MIN; slot < SW_MAP_SLOT_NUM_ENTRIES; slot++) {
    union smartnic_322mhz_bypass_tdest tdest;
    tdest._v = bar2->smartnic_322mhz_regs.bypass_tdest[slot]._v;

    printf ("\t[%u]  %s\t%s\n", slot, switch_map_slot_id_to_name(slot), bypass_tdest_to_name(tdest));
  }
  printf("\n");

  // App0 Logical Output Port Remap to Physical Port
  printf ("Egress Switch APP_0 Port Redirect\n");
  printf ("\tslot Logical\tPhysical\n");
  for (enum switch_map_slot_id slot = SW_MAP_SLOT_MIN; slot < SW_MAP_SLOT_NUM_ENTRIES; slot++) {
    union smartnic_322mhz_app_0_tdest_remap tdest;
    tdest._v = bar2->smartnic_322mhz_regs.app_0_tdest_remap[slot]._v;

    printf ("\t[%u]  %s\t%s\n", slot, switch_map_slot_id_to_name(slot), app_0_tdest_to_name(tdest));
  }
  printf("\n");

  // App1 Logical Output Port Remap to Physical Port
  printf ("Egress Switch APP_1 Port Redirect\n");
  printf ("\tslot Logical\tPhysical\n");
  for (enum switch_map_slot_id slot = SW_MAP_SLOT_MIN; slot < SW_MAP_SLOT_NUM_ENTRIES; slot++) {
    union smartnic_322mhz_app_1_tdest_remap tdest;
    tdest._v = bar2->smartnic_322mhz_regs.app_1_tdest_remap[slot]._v;

    printf ("\t[%u]  %s\t%s\n", slot, switch_map_slot_id_to_name(slot), app_1_tdest_to_name(tdest));
  }
  printf("\n");

  // Egress Switch FIFO Flow Control Thresholds
  printf ("Egress Switch Port FIFO Flow Control Thresholds\n");
  printf ("\tslot Port\tThreshold\n");
  for (enum switch_map_slot_id slot = SW_MAP_SLOT_MIN; slot < SW_MAP_SLOT_NUM_ENTRIES; slot++) {
    printf ("\t[%u]  %s\t%10u\n", slot, switch_map_slot_id_to_name(slot), bar2->smartnic_322mhz_regs.egr_fc_thresh[slot]);
  }
  printf("\n");
}

void cmd_sw(struct argp_state *state)
{
  struct arguments_sw arguments = {0,};
  int  argc   = state->argc - state->next +1;
  char **argv = &state->argv[state->next - 1];
  char *argv0 = argv[0];

  arguments.global = state->input;

  struct argp argp_sw = {
    .options  = argp_options_sw,
    .parser   = parse_opt_sw,
    .args_doc = args_doc_sw,
    .doc      = doc_sw,
  };

  // Temporarily override argv[0] to make error messages show the correct prefix
  argv[0] = malloc(strlen(state->name) + strlen(" sw") + 1);
  if (!argv[0]) {
    argp_failure(state, 1, ENOMEM, 0);
  }
  sprintf(argv[0], "%s sw", state->name);

  // Invoke the subcommand parser
  argp_parse (&argp_sw, argc, argv, ARGP_IN_ORDER, &argc, &arguments);

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

  if (!strcmp(arguments.command, "status")) {
    print_switch_status(bar2);
  } else if (!strcmp(arguments.command, "in-port-rename")) {
    printf ("Applying mappings: %u\n", arguments.map_num_valid);
    for (unsigned int i = 0; i < arguments.map_num_valid; i++) {
      struct switch_map *map = &arguments.map[i];
      printf ("\t[%u]  %s -> %s", i, switch_map_slot_id_to_name(map->a), switch_map_port_id_to_name(map->z));

      union smartnic_322mhz_igr_sw_tid tid;
      if (switch_map_port_id_to_igr_sw_tid(map->z, &tid)) {
	bar2->smartnic_322mhz_regs.igr_sw_tid[map->a]._v = tid._v;
	printf("  OK\n");
      } else {
	printf("  FAIL: Invalid target port name for this table\n");
      }
    }
  } else if (!strcmp(arguments.command, "in-port-connect")) {
    printf ("Applying mappings: %u\n", arguments.map_num_valid);
    for (unsigned int i = 0; i < arguments.map_num_valid; i++) {
      struct switch_map *map = &arguments.map[i];
      printf ("\t[%u]  %s -> %s", i, switch_map_slot_id_to_name(map->a), switch_map_port_id_to_name(map->z));

      union smartnic_322mhz_igr_sw_tdest tdest;
      if (switch_map_port_id_to_igr_sw_tdest(map->z, &tdest)) {
	bar2->smartnic_322mhz_regs.igr_sw_tdest[map->a]._v = tdest._v;
	printf("  OK\n");
      } else {
	printf("  FAIL: Invalid target port name for this table\n");
      }
    }
  } else if (!strcmp(arguments.command, "bypass-connect")) {
    printf ("Applying mappings: %u\n", arguments.map_num_valid);
    for (unsigned int i = 0; i < arguments.map_num_valid; i++) {
      struct switch_map *map = &arguments.map[i];
      printf ("\t[%u]  %s -> %s", i, switch_map_slot_id_to_name(map->a), switch_map_port_id_to_name(map->z));

      union smartnic_322mhz_bypass_tdest tdest;
      if (switch_map_port_id_to_bypass_tdest(map->z, &tdest)) {
	bar2->smartnic_322mhz_regs.bypass_tdest[map->a]._v = tdest._v;
	printf("  OK\n");
      } else {
	printf("  FAIL: Invalid target port name for this table\n");
      }
    }
  } else if (!strcmp(arguments.command, "app0-port-redirect")) {
    printf ("Applying mappings: %u\n", arguments.map_num_valid);
    for (unsigned int i = 0; i < arguments.map_num_valid; i++) {
      struct switch_map *map = &arguments.map[i];
      printf ("\t[%u]  %s -> %s", i, switch_map_slot_id_to_name(map->a), switch_map_port_id_to_name(map->z));

      union smartnic_322mhz_app_0_tdest_remap tdest;
      if (switch_map_port_id_to_app_0_tdest_remap(map->z, &tdest)) {
	bar2->smartnic_322mhz_regs.app_0_tdest_remap[map->a]._v = tdest._v;
	printf("  OK\n");
      } else {
	printf("  FAIL: Invalid target port name for this table\n");
      }
    }
  } else if (!strcmp(arguments.command, "app1-port-redirect")) {
    printf ("Applying mappings: %u\n", arguments.map_num_valid);
    for (unsigned int i = 0; i < arguments.map_num_valid; i++) {
      struct switch_map *map = &arguments.map[i];
      printf ("\t[%u]  %s -> %s", i, switch_map_slot_id_to_name(map->a), switch_map_port_id_to_name(map->z));

      union smartnic_322mhz_app_1_tdest_remap tdest;
      if (switch_map_port_id_to_app_1_tdest_remap(map->z, &tdest)) {
	bar2->smartnic_322mhz_regs.app_1_tdest_remap[map->a]._v = tdest._v;
	printf("  OK\n");
      } else {
	printf("  FAIL: Invalid target port name for this table\n");
      }
    }
  } else if (!strcmp(arguments.command, "out-fifo-fc-thresh")) {
    printf("Unimplemented\n");
  } else {
    fprintf(stderr, "ERROR: %s is not a valid command\n", arguments.command);
  }

  return;
}

