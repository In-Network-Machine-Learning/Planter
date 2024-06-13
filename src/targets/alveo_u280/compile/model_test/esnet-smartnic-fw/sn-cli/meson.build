sources = files(
  [
    'src/sn-cli.c',
    'src/sub-cmac.c',
    'src/sub-dev.c',
    'src/sub-probe.c',
    'src/sub-qdma.c',
    'src/sub-sw.c',
  ]
)

int_incdir = []

cc = meson.get_compiler('c')
libgmp_dep = cc.find_library('gmp')

sn_cli_bin = executable(
  'sn-cli',
  sources,
  include_directories : [
    int_incdir,
  ],
  dependencies : [
    libgmp_dep,
    libopennic_dep,
    libsnp4_dep,
    libsnutil_dep,
    dependency('regmap'),
  ],
  install : true,
)
