#include <string.h>		/* strcmp */
#include "snp4.h"		/* snp4_info_* */
#include "unused.h"		/* UNUSED */

/*
 * This file provides a mock for describing the valid table and action configuration
 * for a fixed, test pipeline.
 */

static struct snp4_info_pipeline snp4_info_pipeline = {
  .tables = {
    {
      .name = "t_p128",
      .endian = SNP4_INFO_TABLE_ENDIAN_BIG,
      .key_bits = 128,
      .matches = {
	{ .type = SNP4_INFO_MATCH_TYPE_PREFIX, .bits = 128 },
      },
      .num_matches = 1,

      .response_bits = 64,
      .actionid_bits = 2,
      .actions = {
	{
	  .name = "a_nop",
	  .param_bits = 0,
	  .num_params = 0,
	},
      },
      .num_actions = 1,

      .priority_required = true,
      .priority_bits = 8,
    },
    {
      .name = "t_b17",
      .endian = SNP4_INFO_TABLE_ENDIAN_BIG,
      .key_bits = 17,
      .matches = {
	{ .type = SNP4_INFO_MATCH_TYPE_BITFIELD, .bits = 17 },
      },
      .num_matches = 1,

      .response_bits = 64,
      .actionid_bits = 2,
      .actions = {
	{
	  .name = "a_nop",
	  .param_bits = 0,
	  .num_params = 0,
	},
      },
      .num_actions = 1,

      .priority_required = false,
    },
    {
      .name = "t_c31",
      .endian = SNP4_INFO_TABLE_ENDIAN_BIG,
      .key_bits = 31,
      .matches = {
	{ .type = SNP4_INFO_MATCH_TYPE_CONSTANT, .bits = 31 },
      },
      .num_matches = 1,

      .response_bits = 64,
      .actionid_bits = 2,
      .actions = {
	{
	  .name = "a_nop",
	  .param_bits = 0,
	  .num_params = 0,
	},
      },
      .num_actions = 1,

      .priority_required = false,
    },
    {
      .name = "t_r16",
      .endian = SNP4_INFO_TABLE_ENDIAN_BIG,
      .key_bits = 16,
      .matches = {
	{ .type = SNP4_INFO_MATCH_TYPE_RANGE, .bits = 16 },
      },
      .num_matches = 1,

      .response_bits = 64,
      .actionid_bits = 2,
      .actions = {
	{
	  .name = "a_nop",
	  .param_bits = 0,
	  .num_params = 0,
	},
      },
      .num_actions = 1,

      .priority_required = true,
      .priority_bits = 8,
    },
    {
      .name = "t_t9",
      .endian = SNP4_INFO_TABLE_ENDIAN_BIG,
      .key_bits = 9,
      .matches = {
	{ .type = SNP4_INFO_MATCH_TYPE_TERNARY, .bits = 9 },
      },
      .num_matches = 1,

      .response_bits = 64,
      .actionid_bits = 2,
      .actions = {
	{
	  .name = "a_nop",
	  .param_bits = 0,
	  .num_params = 0,
	},
      },
      .num_actions = 1,

      .priority_required = true,
      .priority_bits = 8,
    },
    {
      .name = "t_u3",
      .endian = SNP4_INFO_TABLE_ENDIAN_BIG,
      .key_bits = 3,
      .matches = {
	{ .type = SNP4_INFO_MATCH_TYPE_UNUSED, .bits = 3 },
      },
      .num_matches = 1,

      .response_bits = 64,
      .actionid_bits = 2,
      .actions = {
	{
	  .name = "a_nop",
	  .param_bits = 0,
	  .num_params = 0,
	},
      },
      .num_actions = 1,

      .priority_required = true,
      .priority_bits = 8,
    },
    {
      .name = "t_multi",
      .endian = SNP4_INFO_TABLE_ENDIAN_BIG,
      .key_bits = 34,
      .matches = {
	{ .type = SNP4_INFO_MATCH_TYPE_BITFIELD, .bits = 3 },
	{ .type = SNP4_INFO_MATCH_TYPE_CONSTANT, .bits = 3 },
	{ .type = SNP4_INFO_MATCH_TYPE_PREFIX, .bits = 6 },
	{ .type = SNP4_INFO_MATCH_TYPE_RANGE, .bits = 13 },
	{ .type = SNP4_INFO_MATCH_TYPE_TERNARY, .bits = 7 },
	{ .type = SNP4_INFO_MATCH_TYPE_UNUSED, .bits = 2 },
      },
      .num_matches = 6,

      .response_bits = 61,
      .actionid_bits = 0,
      .actions = {
	{
	  .name = "a_nop",
	  .param_bits = 0,
	  .num_params = 0,
	},
	{
	  .name = "a_one",
	  .param_bits = 24,
	  .params = {
	    { .name = "a", .bits = 24 },
	  },
	  .num_params = 1,
	},
	{
	  .name = "a_two",
	  .param_bits = 52,
	  .params = {
	    { .name = "a", .bits = 13 },
	    { .name = "b", .bits = 39 },
	  },
	  .num_params = 2,
	},
	{
	  .name = "a_three",
	  .param_bits = 60,
	  .params = {
	    { .name = "a", .bits = 13 },
	    { .name = "b", .bits = 39 },
	    { .name = "c", .bits = 8 },
	  },
	  .num_params = 3,
	},
      },
      .num_actions = 4,

      .priority_required = true,
      .priority_bits = 3,
    },
  },
  .num_tables = 7,
};

extern enum snp4_status snp4_info_get_pipeline(struct snp4_info_pipeline * pipeline)
{
  memcpy(pipeline, &snp4_info_pipeline, sizeof(*pipeline));

  return SNP4_STATUS_OK;
}
