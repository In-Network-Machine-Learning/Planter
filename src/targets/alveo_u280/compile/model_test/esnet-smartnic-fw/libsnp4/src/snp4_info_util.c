#include <string.h>		/* strcmp */
#include "snp4.h"		/* API, snp4_info_* */

/*
 * Common helper functions for processing an snp4_info_pipeline struct.  They are
 * kept separated from snp4_info.c so these functions can be used in unit tests
 * against a mocked pipeline without triggering hardware library dependencies.
 */

const struct snp4_info_table * snp4_info_get_table_by_name(const struct snp4_info_pipeline * pipeline, const char * table_name)
{
  if (!pipeline) {
    return NULL;
  }
  if (!table_name) {
    return NULL;
  }

  // Find the requested table
  for (unsigned int i = 0; i < pipeline->num_tables; i++) {
    const struct snp4_info_table *info_table = &pipeline->tables[i];
    if (strcmp(info_table->name, table_name) == 0) {
      return info_table;
    }
  }
  return NULL;
}

const struct snp4_info_action * snp4_info_get_action_by_name(const struct snp4_info_table * table, const char * action_name)
{
  if (!table) {
    return NULL;
  }
  if (!action_name) {
    return NULL;
  }

  // Find the requested action
  for (unsigned int i = 0; i < table->num_actions; i++) {
    const struct snp4_info_action *info_action = &table->actions[i];
    if (strcmp(info_action->name, action_name) == 0) {
      return info_action;
    }
  }
  return NULL;
}

