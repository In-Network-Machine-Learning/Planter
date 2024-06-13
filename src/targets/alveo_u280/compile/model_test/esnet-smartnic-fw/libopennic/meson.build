sources = files(
  [
    'src/cmac.c',
    'src/smartnic_probe.c',
    'src/sysmon.c',
    'src/pcie.c',
  ]
)

ext_incdir = include_directories('include')

libopennic = shared_library(
  'opennic',
  sources,
  dependencies : [
    dependency('regmap'),
    libsnutil_dep,
  ],
  include_directories : [
    ext_incdir,
  ],
  install : true,
  soversion : 1,
)

install_headers(
  [
    'include/cmac.h',
    'include/sysmon.h',
    'include/smartnic.h',
  ],
  subdir : 'esnet-smartnic'
)

pkg = import('pkgconfig')
pkg.generate(
  libopennic,
  subdirs : 'esnet-smartnic',
)

libopennic_dep = declare_dependency(
  include_directories : [ext_incdir],
  link_with : [
    libopennic,
    libsnutil,
  ])
