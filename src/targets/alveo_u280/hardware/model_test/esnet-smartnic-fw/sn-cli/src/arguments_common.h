#ifndef ARGUMENTS_COMMON_H
#define ARGUMENTS_COMMON_H

struct arguments_global {
  bool verbose;
  const char *pcieaddr;
};

extern void cmd_cmac(struct argp_state *state);
extern void cmd_dev(struct argp_state *state);
extern void cmd_probe(struct argp_state *state);
extern void cmd_qdma(struct argp_state *state);
extern void cmd_sw(struct argp_state *state);

#endif /* ARGUMENTS_COMMON_H */
