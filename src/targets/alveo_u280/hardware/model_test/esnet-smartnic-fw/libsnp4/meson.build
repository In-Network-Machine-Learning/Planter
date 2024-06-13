sources = files(
  [
    'src/snp4_api.c',
    'src/snp4_info_hw.c',
    'src/snp4_info_util.c',
    'src/snp4_io.c',
    'src/snp4_table.c',
  ]
)

ext_incdir = include_directories('include')
int_incdir = include_directories('src/include')

cc = meson.get_compiler('c')
libgmp_dep = cc.find_library('gmp')

libsnp4 = shared_library(
  'snp4',
  sources,
  dependencies : [
    libgmp_dep,
    dependency('libvitisnetp4drv'),
    libsnutil_dep,
  ],
  include_directories : [
    ext_incdir,
    int_incdir,
  ],
  c_args : [
    #'-DSDNETIO_DEBUG',
    '-DSDNETCONFIG_DEBUG',
  ],
  install : true,
  soversion : 1,
)

install_headers(
  [
    'include/snp4.h',
  ],
  subdir : 'esnet-smartnic'
)

pkg = import('pkgconfig')
pkg.generate(
  libsnp4,
  subdirs : 'esnet-smartnic',
)

libsnp4_dep = declare_dependency(
  include_directories : [ext_incdir],
  link_with : [
    libsnp4,
    libsnutil,
  ])

gtest = dependency('gtest', fallback : ['gtest', 'gtest_main_dep'], main : true, required : true)

snp4_table_ut_src = [
  'src/snp4_info_ut.c',
  'src/snp4_info_util.c',
  'src/snp4_table_ut.cpp',
  'src/snp4_table.c',
]

snp4_table_ut = executable(
  'snp4-table-ut',
  snp4_table_ut_src,
  cpp_args : [
    #'-std=c++2a',
  ],
  dependencies : [
    libgmp_dep,
    libsnutil_dep,
    gtest,
  ],
  include_directories : [
    ext_incdir,
    int_incdir,
  ],
)
test(
  'snp4 table tests',
  snp4_table_ut,
  protocol : 'gtest',
)

