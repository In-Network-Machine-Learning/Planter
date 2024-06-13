#include <iostream>
#include <stdio.h>
#include <stdlib.h>		// exit, EXIT_FAILURE

#include <grpc/grpc.h>
#include <grpcpp/server.h>
#include <grpcpp/server_builder.h>
#include <grpcpp/server_context.h>

#include "sn_p4_v1.grpc.pb.h"

#include "smartnic.h"		// smartnic_map_bar2_by_pciaddr
#include "snp4.h"		// snp4_*

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReader;
using grpc::ServerReaderWriter;
using grpc::Status;
using grpc::StatusCode;

using namespace std;

class SmartnicP4Impl final : public SmartnicP4::Service {
public:
  explicit SmartnicP4Impl(const std::string& pci_address) {
    bar2 = smartnic_map_bar2_by_pciaddr(pci_address.c_str());
    if (bar2 == NULL) {
      std::cout << "Failed to map PCIe register space for device: " << pci_address << std::endl;
      exit(EXIT_FAILURE);
    }

    snp4_handle = snp4_init((uintptr_t) &bar2->sdnet);
    if (snp4_handle == NULL) {
      std::cout << "Failed to initialize snp4/vitisnetp4 library: " << pci_address << std::endl;
      exit(EXIT_FAILURE);
    }

    auto rc = snp4_info_get_pipeline(&pipeline);
    if (rc != SNP4_STATUS_OK) {
      std::cout << "Failed to load snp4 pipeline info: " << rc << std::endl;
      exit(EXIT_FAILURE);
    }
  }

  Status ClearAllTables(ServerContext* /* context */, const ::google::protobuf::Empty* /* empty */, ClearResponse* /* clear_response */) override {
    if (!snp4_reset_all_tables(snp4_handle)) {
      return Status(StatusCode::UNKNOWN, "Failed to reset all tables");
    } else {
      return Status::OK;
    }
  }

  Status ClearOneTable(ServerContext* /* context */, const ClearOneTableRequest* clear_one_table, ClearResponse* /* clear_response */) override {
    if (!snp4_reset_one_table(snp4_handle, const_cast<char *>(clear_one_table->table_name().c_str()))) {
      return Status(StatusCode::UNKNOWN, "Failed to reset table");
    } else {
      return Status::OK;
    }
  }

  Status GetPipelineInfo(ServerContext* /* context */, const ::google::protobuf::Empty* /* empty */, PipelineInfo* PipelineInfoResponse) override {
    // Iterate over all tables
    for (unsigned int tidx = 0; tidx < pipeline.num_tables; tidx++) {
      struct snp4_info_table * t = &pipeline.tables[tidx];

      // Add a new table object to the response
      ::PipelineInfo::TableInfo* pi_table = PipelineInfoResponse->add_tables();

      pi_table->set_name(t->name);

      switch(t->endian) {
      case SNP4_INFO_TABLE_ENDIAN_LITTLE:
	pi_table->set_endian(PipelineInfo_TableInfo_Endian_LITTLE);
	break;
      case SNP4_INFO_TABLE_ENDIAN_BIG:
	pi_table->set_endian(PipelineInfo_TableInfo_Endian_BIG);
	break;
      }

      // Populate the match specs
      for (unsigned int midx = 0; midx < t->num_matches; midx++) {
	struct snp4_info_match * m = &t->matches[midx];

	// Add a new match spec to the response
	::PipelineInfo::TableInfo::MatchSpec* pi_match = pi_table->add_match_specs();

	switch (m->type) {
	case SNP4_INFO_MATCH_TYPE_BITFIELD:
	  pi_match->set_type(PipelineInfo_TableInfo_MatchSpec_MatchType_BITFIELD);
	  break;
	case SNP4_INFO_MATCH_TYPE_CONSTANT:
	  pi_match->set_type(PipelineInfo_TableInfo_MatchSpec_MatchType_CONSTANT);
	  break;
	case SNP4_INFO_MATCH_TYPE_PREFIX:
	  pi_match->set_type(PipelineInfo_TableInfo_MatchSpec_MatchType_PREFIX);
	  break;
	case SNP4_INFO_MATCH_TYPE_RANGE:
	  pi_match->set_type(PipelineInfo_TableInfo_MatchSpec_MatchType_RANGE);
	  break;
	case SNP4_INFO_MATCH_TYPE_TERNARY:
	  pi_match->set_type(PipelineInfo_TableInfo_MatchSpec_MatchType_TERNARY);
	  break;
	case SNP4_INFO_MATCH_TYPE_UNUSED:
	  pi_match->set_type(PipelineInfo_TableInfo_MatchSpec_MatchType_UNUSED);
	  break;
	case SNP4_INFO_MATCH_TYPE_INVALID:
	  // Ignore invalid ones
	  break;
	}
	pi_match->set_bits(m->bits);
      }

      // Populate the action specs
      for (unsigned int aidx = 0; aidx < t->num_actions; aidx++) {
	struct snp4_info_action * a = &t->actions[aidx];

	// Add a new action spec to the response
	::PipelineInfo::TableInfo::ActionSpec* pi_action = pi_table->add_action_specs();

	pi_action->set_name(a->name);

	// Populate the parameters for this action
	for (unsigned int pidx = 0; pidx < a->num_params; pidx++) {
	  struct snp4_info_param * p = &a->params[pidx];

	  // Add a new param spec to the response
	  ::PipelineInfo::TableInfo::ActionSpec::ParameterSpec* pi_param = pi_action->add_parameter_specs();

	  pi_param->set_name(p->name);
	  pi_param->set_bits(p->bits);
	}
      }

      pi_table->set_priority_required(t->priority_required);
      pi_table->set_priority_bits(t->priority_bits);

    }
    return Status::OK;
  }

  Status InsertRule(ServerContext* /* context */, const MatchActionRule* ma, RuleOperationResponse* /* response */) override {
    struct sn_rule rule;

    // Table Name
    rule.table_name = const_cast<char *>(ma->table_name().c_str());

    // Matches
    rule.num_matches = 0;
    for (const Match& match : ma->matches()) {
      struct sn_match * m = &rule.matches[rule.num_matches];

      std::cout << "match: " << match.match_case() << std::endl;
      if (!load_one_match(match, m)) {
	return Status(StatusCode::INVALID_ARGUMENT, "Failed to parse match");
      }

      rule.num_matches++;
    }

    // Action Name
    rule.action_name = const_cast<char *>(ma->action_name().c_str());

    // Action Params
    rule.num_params = 0;
    for (const Param& param : ma->params()) {
      struct sn_param * p = &rule.params[rule.num_params];

      std::cout << "param: " << param.value() << std::endl;
      if (!load_one_param(param, p)) {
	return Status(StatusCode::INVALID_ARGUMENT, "Failed to parse param");
      }

      rule.num_params++;
    }

    // Priority
    rule.priority = ma->priority();

    // Pack the rule's matches and params
    struct sn_pack pack;
    if (snp4_rule_pack(&pipeline, &rule, &pack) != SNP4_STATUS_OK) {
      return Status(StatusCode::INVALID_ARGUMENT, "Failed to pack rule into key/mask and params");
    }

    if (!snp4_table_insert_kma(snp4_handle,
			       rule.table_name,
			       pack.key,
			       pack.key_len,
			       pack.mask,
			       pack.mask_len,
			       rule.action_name,
			       pack.params,
			       pack.params_len,
			       rule.priority,
			       ma->replace())) {
      return Status(StatusCode::INVALID_ARGUMENT, "Failed to insert rule into hardware table");
    }

    return Status::OK;
  }

  Status DeleteRule(ServerContext* /* context */, const MatchOnlyRule* mo, RuleOperationResponse* /* response */) override {
    // Table Name
    auto table_name = const_cast<char *>(mo->table_name().c_str());

    // Find the requested table
    auto table_info = snp4_info_get_table_by_name(&pipeline, table_name);
    if (table_info == NULL) {
      return Status(StatusCode::INVALID_ARGUMENT, "Table not found");
    }

    struct sn_match matches[SNP4_MAX_TABLE_MATCHES];

    // Matches
    uint32_t num_matches = 0;
    for (const Match& match : mo->matches()) {
      struct sn_match * m = &matches[num_matches];

      std::cout << "match: " << match.match_case() << std::endl;
      if (!load_one_match(match, m)) {
	return Status(StatusCode::INVALID_ARGUMENT, "Failed to parse match fields");
      }
      num_matches++;
    }

    // Pack the rule's matches
    struct sn_pack pack;
    snp4_status rc;
    rc = snp4_rule_pack_matches(table_info->matches,
				table_info->key_bits,
				matches,
				num_matches,
				&pack);
    if (rc != SNP4_STATUS_OK) {
      return Status(StatusCode::INVALID_ARGUMENT, "Failed to pack match fields into key/mask");
    }

    if (!snp4_table_delete_k(snp4_handle,
			     table_name,
			     pack.key,
			     pack.key_len,
			     pack.mask,
			     pack.mask_len)) {
      return Status(StatusCode::INVALID_ARGUMENT, "Failed to delete rule from hardware table");
    }

    return Status::OK;
  }

private:
  volatile struct esnet_smartnic_bar2 * volatile bar2;
  void * snp4_handle;
  struct snp4_info_pipeline pipeline;

  bool load_one_param(const Param& param, struct sn_param * p) {
    p->t = SN_PARAM_FORMAT_MPZ;
    if (mpz_init_set_str(p->v.mpz, param.value().c_str(), 0) != 0) {
      mpz_clear(p->v.mpz);
      goto out_parse_error;
    }
    return true;

  out_parse_error:
    return false;
  }

  bool load_one_match(const Match& match, struct sn_match * m) {
    switch(match.match_case()) {
    case Match::MatchCase::kKeyMask:
      m->t = SN_MATCH_FORMAT_KEY_MASK;
      if (mpz_init_set_str(m->v.key_mask.key, match.key_mask().key().c_str(), 0) != 0) {
	mpz_clear(m->v.key_mask.key);
	goto out_parse_error;
      }
      if (mpz_init_set_str(m->v.key_mask.mask, match.key_mask().mask().c_str(), 0) != 0) {
	mpz_clear(m->v.key_mask.key);
	mpz_clear(m->v.key_mask.mask);
	goto out_parse_error;
      }
      break;
    case Match::MatchCase::kKeyOnly:
      m->t = SN_MATCH_FORMAT_KEY_ONLY;
      if (mpz_init_set_str(m->v.key_only.key, match.key_only().key().c_str(), 0) != 0) {
	mpz_clear(m->v.key_only.key);
	goto out_parse_error;
      }
      break;
    case Match::MatchCase::kPrefix:
      m->t = SN_MATCH_FORMAT_PREFIX;
      if (mpz_init_set_str(m->v.prefix.key, match.prefix().key().c_str(), 0) != 0) {
	mpz_clear(m->v.prefix.key);
	goto out_parse_error;
      }
      m->v.prefix.prefix_len = (uint16_t) match.prefix().prefix_len();
      break;
    case Match::MatchCase::kRange:
      m->t = SN_MATCH_FORMAT_RANGE;
      m->v.range.lower = (uint16_t) match.range().lower();
      m->v.range.upper = (uint16_t) match.range().upper();
      break;
    case Match::MatchCase::kUnused:
      m->t = SN_MATCH_FORMAT_UNUSED;
      break;
    default:
      goto out_parse_error;
      break;
    }

    return true;

  out_parse_error:
    return false;
  }
};

void RunServer(const std::string& pci_address) {

  // Verify that the version of the library that we linked with matches the version of the
  // header files that we compiled against.
  GOOGLE_PROTOBUF_VERIFY_VERSION;

  std::string server_address("0.0.0.0:50051");
  SmartnicP4Impl service(pci_address);

  ServerBuilder builder;
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);
  std::unique_ptr<Server> server(builder.BuildAndStart());
  std::cout << "Server listening on " << server_address << std::endl;
  server->Wait();

  // Delete all global objects allocated by libprotobuf to keep memory checkers happy
  google::protobuf::ShutdownProtobufLibrary();
}

int main(int argc, char *argv[])
{
  // Convert args into a vector of strings
  std::vector<std::string> args(argv + 1, argv + argc);

  if (args.size() < 1) {
    std::cout << "Missing PCIe address parameter" << std::endl;
    exit(EXIT_FAILURE);
  }

  RunServer(args[0]);

  return 0;
}
