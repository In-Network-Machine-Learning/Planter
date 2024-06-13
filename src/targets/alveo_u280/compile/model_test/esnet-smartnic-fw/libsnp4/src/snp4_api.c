//
// Copyright (c) 2021, The Regents of the University of California,
// through Lawrence Berkeley National Laboratory (subject to receipt of
// any required approvals from the U.S. Dept. of Energy).  All rights
// reserved.
//

#include <stdio.h>		/* fprintf */
#include "snp4.h"		/* API */
#include "sdnet_0_defs.h"	/* XilVitisNetP4TargetConfig_sdnet_0 */
#include "snp4_io.h"		/* snp4_io_reg_* */
#include "unused.h"		/* UNUSED() */

struct snp4_user_context {
  uintptr_t base_addr;
};

static XilVitisNetP4ReturnType device_write(XilVitisNetP4EnvIf *EnvIfPtr, XilVitisNetP4AddressType address, uint32_t data) {
    // Validate inputs
    if (NULL == EnvIfPtr) {
        return XIL_VITIS_NET_P4_GENERAL_ERR_NULL_PARAM;
    }
    if (NULL == EnvIfPtr->UserCtx)	{
        return XIL_VITIS_NET_P4_GENERAL_ERR_INTERNAL_ASSERTION;
    }

    // Recover virtual base address from user context
    struct snp4_user_context * user_ctx;
    user_ctx = (struct snp4_user_context *)EnvIfPtr->UserCtx;

    // Do the operation
    snp4_io_reg_write(user_ctx->base_addr, address, data);

    return XIL_VITIS_NET_P4_SUCCESS;
}

static XilVitisNetP4ReturnType device_read(XilVitisNetP4EnvIf *EnvIfPtr, XilVitisNetP4AddressType address, uint32_t *dataPtr) {
    // Validate inputs
    if (EnvIfPtr == NULL) {
        return XIL_VITIS_NET_P4_GENERAL_ERR_NULL_PARAM;
    }
    if (EnvIfPtr->UserCtx == NULL) {
        return XIL_VITIS_NET_P4_GENERAL_ERR_INTERNAL_ASSERTION;
    }
    if (dataPtr == NULL) {
        return XIL_VITIS_NET_P4_GENERAL_ERR_INTERNAL_ASSERTION;
    }

    // Recover virtual base address from user context
    struct snp4_user_context * user_ctx;
    user_ctx = (struct snp4_user_context *)EnvIfPtr->UserCtx;

    // Do the operation
    snp4_io_reg_read(user_ctx->base_addr, address, dataPtr);

    return XIL_VITIS_NET_P4_SUCCESS;
}

static XilVitisNetP4ReturnType log_info(XilVitisNetP4EnvIf *UNUSED(EnvIfPtr), const char *MessagePtr)
{
  fprintf(stdout, "%s\n", MessagePtr);

  return XIL_VITIS_NET_P4_SUCCESS;
}

static XilVitisNetP4ReturnType log_error(XilVitisNetP4EnvIf *UNUSED(EnvIfPtr), const char *MessagePtr)
{
  fprintf(stderr, "%s\n", MessagePtr);

  return XIL_VITIS_NET_P4_SUCCESS;
}

void * snp4_init(uintptr_t snp4_base_addr)
{
  struct snp4_user_context * snp4_user;
  snp4_user = (struct snp4_user_context *) calloc(1, sizeof(struct snp4_user_context));
  if (snp4_user == NULL) {
    goto out_fail;
  }
  snp4_user->base_addr = snp4_base_addr;

  XilVitisNetP4EnvIf * vitisnetp4_env;
  vitisnetp4_env = (XilVitisNetP4EnvIf *) calloc(1, sizeof(XilVitisNetP4EnvIf));
  if (vitisnetp4_env == NULL) {
    goto out_fail_user;
  }

  XilVitisNetP4TargetCtx * vitisnetp4_target;
  vitisnetp4_target = (XilVitisNetP4TargetCtx *) calloc(1, sizeof(XilVitisNetP4EnvIf));
  if (vitisnetp4_target == NULL) {
    goto out_fail_env;
  }

  // Initialize the vitisnetp4 env
  if (XilVitisNetP4StubEnvIf(vitisnetp4_env) != XIL_VITIS_NET_P4_SUCCESS) {
    goto out_fail_target;
  }
  vitisnetp4_env->WordWrite32 = (XilVitisNetP4WordWrite32Fp) &device_write;
  vitisnetp4_env->WordRead32  = (XilVitisNetP4WordRead32Fp)  &device_read;
  vitisnetp4_env->UserCtx     = (XilVitisNetP4UserCtxType)   snp4_user;
  vitisnetp4_env->LogError    = (XilVitisNetP4LogFp)         &log_error;
  vitisnetp4_env->LogInfo     = (XilVitisNetP4LogFp)         &log_info;

  // Initialize the vitisnetp4 target
  if (XilVitisNetP4TargetInit(vitisnetp4_target, vitisnetp4_env, &XilVitisNetP4TargetConfig_sdnet_0) != XIL_VITIS_NET_P4_SUCCESS) {
    goto out_fail_target;
  }

  return (void *) vitisnetp4_target;

 out_fail_target:
  free(vitisnetp4_target);
 out_fail_env:
  free(vitisnetp4_env);
 out_fail_user:
  free(snp4_user);
 out_fail:
  return NULL;
}

bool snp4_deinit(void * snp4_handle)
{
  XilVitisNetP4TargetCtx * vitisnetp4_target = (XilVitisNetP4TargetCtx *) snp4_handle;

  if (XilVitisNetP4TargetExit(vitisnetp4_target) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  return true;
}

bool snp4_reset_all_tables(void * snp4_handle)
{
  XilVitisNetP4TargetCtx * vitisnetp4_target = (XilVitisNetP4TargetCtx *) snp4_handle;

  // Look up the number of tables in the design
  uint32_t num_tables;
  if (XilVitisNetP4TargetGetTableCount(vitisnetp4_target, &num_tables) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  // Reset all of the tables in the design
  for (uint32_t i = 0; i < num_tables; i++) {
    XilVitisNetP4TableCtx * table;
    if (XilVitisNetP4TargetGetTableByIndex(vitisnetp4_target, i, &table) != XIL_VITIS_NET_P4_SUCCESS) {
      return false;
    }
    if (XilVitisNetP4TableReset(table) != XIL_VITIS_NET_P4_SUCCESS) {
      return false;
    }
  }

  return true;
}

bool snp4_reset_one_table(void * snp4_handle, const char * table_name)
{
  XilVitisNetP4TargetCtx * vitisnetp4_target = (XilVitisNetP4TargetCtx *) snp4_handle;

  XilVitisNetP4TableCtx * table;
  if (XilVitisNetP4TargetGetTableByName(vitisnetp4_target, (char *)table_name, &table) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  if (XilVitisNetP4TableReset(table) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  return true;
}

bool snp4_table_insert_kma(void * snp4_handle,
			   const char * table_name,
			   uint8_t * key,
			   size_t UNUSED(key_len),
			   uint8_t * mask,
			   size_t UNUSED(mask_len),
			   const char * action_name,
			   uint8_t * params,
			   size_t UNUSED(params_len),
			   uint32_t priority,
			   bool replace)
{
  XilVitisNetP4TargetCtx * vitisnetp4_target = (XilVitisNetP4TargetCtx *) snp4_handle;

  // Get a handle for the target table
  XilVitisNetP4TableCtx * table;
  if (XilVitisNetP4TargetGetTableByName(vitisnetp4_target, (char *)table_name, &table) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  // Convert the action name to an id
  uint32_t action_id;
  if (XilVitisNetP4TableGetActionId(table, (char *)action_name, &action_id) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  XilVitisNetP4TableMode table_mode;
  if (XilVitisNetP4TableGetMode(table, &table_mode) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  // Certain table modes insist on a NULL mask parameter
  switch (table_mode) {
  case XIL_VITIS_NET_P4_TABLE_MODE_DCAM:
  case XIL_VITIS_NET_P4_TABLE_MODE_BCAM:
  case XIL_VITIS_NET_P4_TABLE_MODE_TINY_BCAM:
    // Mask parameter must be NULL for these table modes
    mask = NULL;
    break;
  default:
    // All other table modes require the mask
    break;
  }

  if (replace) {
    /* Replace an existing entry */
    if (XilVitisNetP4TableUpdate(table, key, mask, action_id, params) != XIL_VITIS_NET_P4_SUCCESS) {
      return false;
    }
  } else {
    /* Insert an entirely new entry */
    if (XilVitisNetP4TableInsert(table, key, mask, priority, action_id, params) != XIL_VITIS_NET_P4_SUCCESS) {
      return false;
    }
  }

  return true;
}

bool snp4_table_delete_k(void * snp4_handle,
			 const char * table_name,
			 uint8_t * key,
			 size_t    UNUSED(key_len),
			 uint8_t * mask,
			 size_t    UNUSED(mask_len))
{
  XilVitisNetP4TargetCtx * vitisnetp4_target = (XilVitisNetP4TargetCtx *) snp4_handle;

  // Get a handle for the target table
  XilVitisNetP4TableCtx * table;
  if (XilVitisNetP4TargetGetTableByName(vitisnetp4_target, (char *)table_name, &table) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  XilVitisNetP4TableMode table_mode;
  if (XilVitisNetP4TableGetMode(table, &table_mode) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  // Certain table modes insist on a NULL mask parameter
  switch (table_mode) {
  case XIL_VITIS_NET_P4_TABLE_MODE_DCAM:
  case XIL_VITIS_NET_P4_TABLE_MODE_BCAM:
  case XIL_VITIS_NET_P4_TABLE_MODE_TINY_BCAM:
    // Mask parameter must be NULL for these table modes
    mask = NULL;
    break;
  default:
    // All other table modes require the mask
    break;
  }

  if (XilVitisNetP4TableDelete(table, key, mask) != XIL_VITIS_NET_P4_SUCCESS) {
    return false;
  }

  return true;
}
