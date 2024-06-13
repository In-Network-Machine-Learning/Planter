#include "gtest/gtest.h"
#include <gmp.h>
#include <string.h>

extern "C" {
#include "snp4.h"		/* API */
}

static void display_pack(struct sn_pack * pack)
{
  std::cout << std::hex << std::setfill('0');

  std::cout << "Key   : ";
  if (pack->key != NULL) {
    for (unsigned int i = 0; i < pack->key_len; i++) {
      std::cout << std::setw(2) << static_cast<unsigned>(pack->key[i]);
    }
    std::cout << std::endl;
  } else {
    std::cout << "null" << std::endl;
  }

  std::cout << "Mask  : ";
  if (pack->mask != NULL) {
    for (unsigned int i = 0; i < pack->mask_len; i++) {
      std::cout << std::setw(2) << static_cast<unsigned>(pack->mask[i]);
    }
    std::cout << std::endl;
  } else {
    std::cout << "null" << std::endl;
  }

  std::cout << "Params: ";
  if (pack->params != NULL) {
    for (unsigned int i = 0; i < pack->params_len; i++) {
      std::cout << std::setw(2) << static_cast<unsigned>(pack->params[i]);
    }
    std::cout << std::endl;
  } else {
    std::cout << "null" << std::endl;
  }
};

class SNP4TableTest : public ::testing::Test {
protected:
  SNP4TableTest() {
    rule.num_matches = 0;
    rule.priority = 0;

    rule.num_params = 0;

    snp4_info_get_pipeline(&pipeline);
  }

  void TearDown() override {
    display_pack(&pack);
  }

  struct sn_rule rule;
  struct sn_pack pack;

  enum snp4_status rc;

  struct snp4_info_pipeline pipeline;
};

class SNP4TablePrefixTest : public ::SNP4TableTest {
protected:
  void SetUp() override {
    rule.table_name = strdup("t_p128");
    rule.action_name = strdup("a_nop");
  }
};

TEST_F(SNP4TablePrefixTest, PackPrefixFieldAsKeyMask) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x000aabbccddeeff00112233445566778", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0xffffe000000000000000000000000000", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TablePrefixTest, PackPrefixFieldAsPrefixMin) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_PREFIX;
  mpz_init_set_str(m->v.prefix.key,  "0xaabbccddeeff00112233445566778", 0);
  m->v.prefix.prefix_len = 0;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TablePrefixTest, PackPrefixFieldAsPrefixMax) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_PREFIX;
  mpz_init_set_str(m->v.prefix.key,  "0xaabbccddeeff00112233445566778", 0);
  m->v.prefix.prefix_len = 128;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TablePrefixTest, PackPrefixFieldAsPrefixMid) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_PREFIX;
  mpz_init_set_str(m->v.prefix.key,  "0xaabbccddeeff00112233445566778", 0);
  m->v.prefix.prefix_len = 19;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TablePrefixTest, PackPrefixFieldAsKeyMaskTooWide) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x000aabbccddeeff00112233445566778", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x1ffffe000000000000000000000000000", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_MASK_TOO_BIG, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TablePrefixTest, PackPrefixFieldAsKey) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_ONLY;
  mpz_init_set_str(m->v.key_only.key,  "0xaabbccddeeff00112233445566778", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TablePrefixTest, PackPrefixWithSparseMask) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x000aabbccddeeff00112233445566778", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0xffffe00000000000ffff000000000000", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_INVALID_PREFIX_MASK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TablePrefixTest, PackPrefixWithInvalidPrefixLen) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_PREFIX;
  mpz_init_set_str(m->v.prefix.key,  "0xaabbccddeeff00112233445566778", 0);
  m->v.prefix.prefix_len = 999;

  ASSERT_EQ(SNP4_STATUS_MATCH_MASK_TOO_WIDE, snp4_rule_pack(&pipeline, &rule, &pack));
};

class SNP4TableBitfieldTest : public ::SNP4TableTest {
protected:
  void SetUp() override {
    rule.table_name = strdup("t_b17");
    rule.action_name = strdup("a_nop");
  }
};

TEST_F(SNP4TableBitfieldTest, PackBitfieldFieldAsKeyMaskOnes) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x0103e", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x1ffff", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableBitfieldTest, PackBitfieldFieldAsKeyMaskZero) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x0103e", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x00000", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableBitfieldTest, PackBitfieldFieldAsKeyTooWide) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_ONLY;
  mpz_init_set_str(m->v.key_only.key,  "0x3e0fe", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_KEY_TOO_BIG, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableBitfieldTest, PackBitfieldFieldAsSparseKeyMask) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x0103e", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x0ff00", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_INVALID_BITFIELD_MASK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableBitfieldTest, PackBitfieldFieldAsKey) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_ONLY;
  mpz_init_set_str(m->v.key_only.key,  "0xee", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TableBitfieldTest, PackBitfieldFieldAsPrefixOnes) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_PREFIX;
  mpz_init_set_str(m->v.prefix.key,  "0x1111", 0);
  m->v.prefix.prefix_len = 17;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TableBitfieldTest, PackBitfieldFieldAsPrefixZero) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_PREFIX;
  mpz_init_set_str(m->v.prefix.key,  "0x1111", 0);
  m->v.prefix.prefix_len = 0;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

class SNP4TableConstantTest : public ::SNP4TableTest {
protected:
  void SetUp() override {
    rule.table_name = strdup("t_c31");
    rule.action_name = strdup("a_nop");
  }
};

TEST_F(SNP4TableConstantTest, PackConstantFieldAsKey) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_ONLY;
  mpz_init_set_str(m->v.key_only.key,  "0x7bcdef01", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
};

TEST_F(SNP4TableConstantTest, PackConstantFieldAsSparseKeyMask) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x7bcdef01", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x00ffff00", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_INVALID_CONSTANT_MASK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableConstantTest, PackConstantFieldAsKeyMaskZero) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x7bcdef01", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x00000000", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_INVALID_CONSTANT_MASK, snp4_rule_pack(&pipeline, &rule, &pack));
}

class SNP4TableRangeTest : public ::SNP4TableTest {
protected:
  void SetUp() override {
    rule.table_name = strdup("t_r16");
    rule.action_name = strdup("a_nop");
  }
};

TEST_F(SNP4TableRangeTest, PackRangeFieldAsRange) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_RANGE;
  m->v.range.lower = 0x1234;
  m->v.range.upper = 0x1239;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableRangeTest, PackRangeFieldAsKeyMask) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x1234", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x1239", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableRangeTest, PackRangeFieldAsKey) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_ONLY;
  mpz_init_set_str(m->v.key_only.key,  "0x1234", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableRangeTest, PackRangeFieldAsRangeEqual) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_RANGE;
  m->v.range.lower = 0x1234;
  m->v.range.upper = 0x1234;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableRangeTest, PackRangeFieldAsRangeFlipped) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_RANGE;
  m->v.range.lower = 0x1239;
  m->v.range.upper = 0x1234;

  ASSERT_EQ(SNP4_STATUS_MATCH_INVALID_RANGE_MASK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableRangeTest, PackRangeFieldAsKeyMaskTooBig) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x1234", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0xf1239", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_MASK_TOO_BIG, snp4_rule_pack(&pipeline, &rule, &pack));
}

class SNP4TableTernaryTest : public ::SNP4TableTest {
protected:
  void SetUp() override {
    rule.table_name = strdup("t_t9");
    rule.action_name = strdup("a_nop");
  }
};

TEST_F(SNP4TableTernaryTest, PackTernaryFieldAsKeyMask) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x030", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x101", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

class SNP4TableUnusedTest : public ::SNP4TableTest {
protected:
  void SetUp() override {
    rule.table_name = strdup("t_u3");
    rule.action_name = strdup("a_nop");
  }
};

TEST_F(SNP4TableUnusedTest, PackUnusedFieldAsKey) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_ONLY;
  mpz_init_set_str(m->v.key_only.key,  "0x2", 0);

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableUnusedTest, PackUnusedFieldUnused) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_UNUSED;

  ASSERT_EQ(SNP4_STATUS_OK, snp4_rule_pack(&pipeline, &rule, &pack));
}

TEST_F(SNP4TableUnusedTest, PackUnusedFieldAsKeyMaskNonZero) {
  struct sn_match * m;

  m = &rule.matches[rule.num_matches++];
  m->t = SN_MATCH_FORMAT_KEY_MASK;
  mpz_init_set_str(m->v.key_mask.key,  "0x2", 0);
  mpz_init_set_str(m->v.key_mask.mask, "0x3", 0);

  ASSERT_EQ(SNP4_STATUS_MATCH_INVALID_UNUSED_MASK, snp4_rule_pack(&pipeline, &rule, &pack));
}

