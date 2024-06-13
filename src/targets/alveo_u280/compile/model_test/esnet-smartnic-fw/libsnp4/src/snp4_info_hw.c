#include <stdio.h>
#include <string.h>		/* strdup */
#include "sdnet_0_defs.h"	/* XilVitisNetP4TargetConfig_sdnet_0 */
#include "snp4.h"		/* API */
#include "array_size.h"		/* ARRAY_SIZE */

static const char * tabs(unsigned int indent)
{
  switch (indent) {
  case 0:  return "";
  case 1:  return "\t";
  case 2:  return "\t\t";
  case 3:  return "\t\t\t";
  case 4:  return "\t\t\t\t";
  case 5:  return "\t\t\t\t\t";
  case 6:  return "\t\t\t\t\t\t";
  default: return "\t\t\t\t\t\t\t";
  }
}

static const char * vitisnetp4_endian_str(XilVitisNetP4Endian endian)
{
  switch (endian) {
  case XIL_VITIS_NET_P4_LITTLE_ENDIAN: return "Little Endian";
  case XIL_VITIS_NET_P4_BIG_ENDIAN:    return "Big Endian";
  default: return "??";
  }
}

static const char * vitisnetp4_table_mode_str(XilVitisNetP4TableMode mode)
{
  switch (mode) {
  case XIL_VITIS_NET_P4_TABLE_MODE_BCAM:      return "BCAM";
  case XIL_VITIS_NET_P4_TABLE_MODE_STCAM:     return "STCAM";
  case XIL_VITIS_NET_P4_TABLE_MODE_TCAM:      return "TCAM";
  case XIL_VITIS_NET_P4_TABLE_MODE_DCAM:      return "DCAM";
  case XIL_VITIS_NET_P4_TABLE_MODE_TINY_BCAM: return "Tiny BCAM";
  case XIL_VITIS_NET_P4_TABLE_MODE_TINY_TCAM: return "Tiny TCAM";
  default: return "??";
  }
}

static const char * vitisnetp4_cam_optimization_type(XilVitisNetP4CamOptimizationType opt_type)
{
  switch (opt_type) {
  case XIL_VITIS_NET_P4_CAM_OPTIMIZE_NONE:    return "None";
  case XIL_VITIS_NET_P4_CAM_OPTIMIZE_RAM:     return "RAM";
  case XIL_VITIS_NET_P4_CAM_OPTIMIZE_LOGIC:   return "Logic";
  case XIL_VITIS_NET_P4_CAM_OPTIMIZE_ENTRIES: return "Entries";
  case XIL_VITIS_NET_P4_CAM_OPTIMIZE_MASKS:   return "Masks";
  default: return "??";
  }
}

static const char * vitisnetp4_cam_mem_type(XilVitisNetP4CamMemType mem_type)
{
  switch (mem_type) {
  case XIL_VITIS_NET_P4_CAM_MEM_AUTO: return "Auto";
  case XIL_VITIS_NET_P4_CAM_MEM_BRAM: return "BRAM";
  case XIL_VITIS_NET_P4_CAM_MEM_URAM: return "URAM";
  case XIL_VITIS_NET_P4_CAM_MEM_HBM:  return "HBM";
  case XIL_VITIS_NET_P4_CAM_MEM_RAM:  return "RAM";
  default: return "??";
  }
}

static void vitisnetp4_print_cam_config(XilVitisNetP4CamConfig *cc, unsigned int indent)
{
  printf("%sBaseAddr: 0x%08lx\n", tabs(indent), cc->BaseAddr);
  printf("%sFormatString: %s\n", tabs(indent), cc->FormatStringPtr);
  printf("%sNumEntries: %u\n", tabs(indent), cc->NumEntries);
  printf("%sRamFrequencyHz: %u\n", tabs(indent), cc->RamFrequencyHz);
  printf("%sLookupFrequencyHz: %u\n", tabs(indent), cc->LookupFrequencyHz);
  printf("%sLookupsPerSec: %u\n", tabs(indent), cc->LookupsPerSec);
  printf("%sResponseSizeBits: %u\n", tabs(indent), cc->ResponseSizeBits);
  printf("%sPrioritySizeBits: %u\n", tabs(indent), cc->PrioritySizeBits);
  printf("%sNumMasks: %u\n", tabs(indent), cc->NumMasks);
  printf("%sEndian: %s\n", tabs(indent), vitisnetp4_endian_str(cc->Endian));
  printf("%sMemType: %s\n", tabs(indent), vitisnetp4_cam_mem_type(cc->MemType));
  printf("%sRamSizeKbytes: %u\n", tabs(indent), cc->RamSizeKbytes);
  printf("%sOptimizationType: %s\n", tabs(indent), vitisnetp4_cam_optimization_type(cc->OptimizationType));
}

static void vitisnetp4_print_param(XilVitisNetP4Attribute *attr, unsigned int indent)
{
  printf("%s%3u %s\n", tabs(indent), attr->Value, attr->NameStringPtr);
}

static void vitisnetp4_print_action(XilVitisNetP4Action *a, unsigned int indent)
{
  printf("%sName: %s\n", tabs(indent), a->NameStringPtr);
  printf("%sParameters: [n=%u]\n", tabs(indent), a->ParamListSize);
  for (unsigned int pidx = 0; pidx < a->ParamListSize; pidx++) {
    XilVitisNetP4Attribute *attr = &a->ParamListPtr[pidx];
    vitisnetp4_print_param(attr, indent+1);
  }
}

static void vitisnetp4_print_table_config(XilVitisNetP4TableConfig *tc, unsigned int indent)
{
  printf("%sEndian: %s\n", tabs(indent), vitisnetp4_endian_str(tc->Endian));
  printf("%sMode: %s\n", tabs(indent), vitisnetp4_table_mode_str(tc->Mode));
  printf("%sKeySizeBits: %u\n", tabs(indent), tc->KeySizeBits);
  printf("%sCamConfig:\n", tabs(indent));
  vitisnetp4_print_cam_config(&tc->CamConfig, indent+1);
  printf("%sActionIdWidthBits: %u\n", tabs(indent), tc->ActionIdWidthBits);

  printf("%sActions: [n=%u]\n", tabs(indent), tc->ActionListSize);
  for (unsigned int aidx = 0; aidx < tc->ActionListSize; aidx++) {
    XilVitisNetP4Action *a = tc->ActionListPtr[aidx];
    vitisnetp4_print_action(a, indent+1);
  }
}

static void vitisnetp4_print_target_table_config(XilVitisNetP4TargetTableConfig *ttc, unsigned int indent)
{
  printf("%sName: %s\n", tabs(indent), ttc->NameStringPtr);

  printf("%sConfig:\n", tabs(indent));
  vitisnetp4_print_table_config(&ttc->Config, indent+1);
}

void snp4_print_target_config (void)
{
  struct XilVitisNetP4TargetConfig *tcfg = &XilVitisNetP4TargetConfig_sdnet_0;

  printf("Endian: %s\n", vitisnetp4_endian_str(tcfg->Endian));
  printf("Tables: [n=%u]\n", tcfg->TableListSize);
  for (unsigned int tidx = 0; tidx < tcfg->TableListSize; tidx++) {
    XilVitisNetP4TargetTableConfig *t = tcfg->TableListPtr[tidx];
    vitisnetp4_print_target_table_config(t, 0);
  }
}

static enum snp4_status snp4_info_get_params(struct snp4_info_param * params, uint16_t max_params, uint16_t * num_params, uint16_t * param_bits, XilVitisNetP4Attribute cfg_params[], unsigned int size)
{
  if (size > max_params) {
    return SNP4_STATUS_INFO_TOO_MANY_PARAMS;
  }

  *num_params = size;

  *param_bits = 0;
  for (unsigned int pidx = 0; pidx < size; pidx++) {
    XilVitisNetP4Attribute *xp = &cfg_params[pidx];
    struct snp4_info_param * param = &params[pidx];

    param->name = xp->NameStringPtr;
    param->bits = xp->Value;

    // Accumulate the total number of bits in the parameters for this action
    *param_bits += xp->Value;
  }

  return SNP4_STATUS_OK;
}

static enum snp4_status snp4_info_get_actions(struct snp4_info_action * actions, uint16_t max_actions, uint16_t * num_actions, XilVitisNetP4Action * cfg_actions[], unsigned int size)
{
  static enum snp4_status rc;

  if (size > max_actions) {
    return SNP4_STATUS_INFO_TOO_MANY_ACTIONS;
  }

  *num_actions = size;

  for (unsigned int aidx = 0; aidx < size; aidx++) {
    XilVitisNetP4Action *xa = cfg_actions[aidx];
    struct snp4_info_action * action = &actions[aidx];

    action->name = xa->NameStringPtr;

    rc = snp4_info_get_params(action->params,
			      ARRAY_SIZE(action->params),
			      &action->num_params,
			      &action->param_bits,
			      xa->ParamListPtr,
			      xa->ParamListSize);
    if (rc != SNP4_STATUS_OK) {
      return rc;
    }
  }

  return SNP4_STATUS_OK;
}

static enum snp4_status snp4_info_get_matches(struct snp4_info_match * matches, uint16_t max_matches, uint16_t * num_matches, bool * priority_required, XilVitisNetP4CamConfig *cfg_cam) {

  // Pass 1:
  //   Parse this table's FormatString once to determine the number of match fields only
  if (cfg_cam->FormatStringPtr[0] == '\0') {
    // Empty format string means no fields
    *num_matches = 0;
  } else {
    // We have at least 1 match field
    *num_matches = 1;
    // Now add 1 for every field separator
    for (unsigned int i = 0; cfg_cam->FormatStringPtr[i]; i++) {
      if (cfg_cam->FormatStringPtr[i] == ':') {
	(*num_matches)++;
      }
    }
  }

  if (*num_matches > max_matches) {
    return SNP4_STATUS_INFO_TOO_MANY_MATCHES;
  }

  // Pass 2:
  //   Record the field format and size for each field spec in the FormatString
  char *table_fmt = strdup(cfg_cam->FormatStringPtr);
  char *table_fmt_cursor = table_fmt;

  // Assume no priority field is required
  *priority_required = false;

  // NOTE: The HW format string describes the fields of the key from lsbs up to msbs.
  //       The p4 table definitions (which the user sees) describe the fields from msbs down to lsbs.
  //       We want the user to provide the fields in the same order that they occur in the p4 table
  //       since that is most natural to the user *and* the code in snp4_table.c that packs the matches
  //       also wants to pack the fields from the user from msbs down to lsbs.  Pack the matches[] array
  //       in reverse order relative to the HW format string.
  for (unsigned int i = 0; i < *num_matches; i++) {
    struct snp4_info_match * match = &matches[*num_matches - 1 - i];

    char * field_fmt = strsep(&table_fmt_cursor, ":");
    if (field_fmt == NULL) {
      // Something went wrong -- we ran out of fields even though we just counted them above ??
      match->type = SNP4_INFO_MATCH_TYPE_INVALID;
      match->bits = 0;
      continue;
    }

    unsigned int field_size;
    char field_type;
    int matched = sscanf(field_fmt, "%u%c", &field_size, &field_type);
    if (matched != 2) {
      // Field format is not in the expected form
      match->type = SNP4_INFO_MATCH_TYPE_INVALID;
      match->bits = 0;
      continue;
    }

    match->bits = field_size;

    switch(field_type) {
    case 'b':
      // Bitmask Field Type
      match->type = SNP4_INFO_MATCH_TYPE_BITFIELD;
      break;
    case 'c':
      // Constant Field Type
      match->type = SNP4_INFO_MATCH_TYPE_CONSTANT;
      break;
    case 'p':
      // Prefix Field Type
      match->type = SNP4_INFO_MATCH_TYPE_PREFIX;
      *priority_required = true;
      break;
    case 'r':
      // Range Field Type
      match->type = SNP4_INFO_MATCH_TYPE_RANGE;
      *priority_required = true;
      break;
    case 't':
      // Ternary Field Type
      match->type = SNP4_INFO_MATCH_TYPE_TERNARY;
      *priority_required = true;
      break;
    case 'u':
      // Unused Field Type
      match->type = SNP4_INFO_MATCH_TYPE_UNUSED;
      break;
    default:
      // Unknown Field Type
      match->type = SNP4_INFO_MATCH_TYPE_INVALID;
      match->bits = 0;
      break;
    }
  }
  return SNP4_STATUS_OK;
}

static enum snp4_status snp4_info_get_tables(struct snp4_info_table * tables, uint16_t max_tables, uint16_t * num_tables, XilVitisNetP4TargetTableConfig * cfg_tables[], unsigned int size) {
  enum snp4_status rc;

  // Make sure our info struct will hold all of this pipeline's tables
  if (size > max_tables) {
    return SNP4_STATUS_INFO_TOO_MANY_TABLES;
  }
  *num_tables = size;

  for (unsigned int tidx = 0; tidx < size; tidx++) {
    XilVitisNetP4TargetTableConfig *xt = cfg_tables[tidx];
    struct snp4_info_table * table = &tables[tidx];

    table->name = xt->NameStringPtr;

    switch (xt->Config.Endian) {
    case XIL_VITIS_NET_P4_LITTLE_ENDIAN:
      table->endian = SNP4_INFO_TABLE_ENDIAN_LITTLE;
      break;
    case XIL_VITIS_NET_P4_BIG_ENDIAN:
      table->endian = SNP4_INFO_TABLE_ENDIAN_BIG;
      break;
    default:
      return SNP4_STATUS_INFO_INVALID_ENDIAN;
      break;
    }

    table->key_bits = xt->Config.KeySizeBits;
    table->response_bits = xt->Config.CamConfig.ResponseSizeBits;
    table->priority_bits = xt->Config.CamConfig.PrioritySizeBits;
    table->actionid_bits = xt->Config.ActionIdWidthBits;

    rc = snp4_info_get_matches(table->matches,
			       ARRAY_SIZE(table->matches),
			       &table->num_matches,
			       &table->priority_required,
			       &xt->Config.CamConfig);
    if (rc != SNP4_STATUS_OK) {
      return rc;
    }

    rc = snp4_info_get_actions(table->actions,
			       ARRAY_SIZE(table->actions),
			       &table->num_actions,
			       xt->Config.ActionListPtr,
			       xt->Config.ActionListSize);
    if (rc != SNP4_STATUS_OK) {
      return rc;
    }
  }

  return SNP4_STATUS_OK;
}

enum snp4_status snp4_info_get_pipeline(struct snp4_info_pipeline * pipeline)
{
  struct XilVitisNetP4TargetConfig *cfg = &XilVitisNetP4TargetConfig_sdnet_0;

  return snp4_info_get_tables(pipeline->tables,
			      ARRAY_SIZE(pipeline->tables),
			      &pipeline->num_tables,
			      cfg->TableListPtr,
			      cfg->TableListSize);
}
