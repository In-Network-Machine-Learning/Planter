sources = files(
  [
  ]
)

ext_incdir = include_directories('include')

libsnutil = shared_library(
  'snutil',
  sources,
  include_directories : [
    ext_incdir,
  ],
  install : true,
  soversion : 1,
)

install_headers(
  [
    'include/array_size.h',
    'include/memory-barriers.h',
    'include/unused.h',
  ],
  subdir : 'esnet-smartnic'
)

pkg = import('pkgconfig')
pkg.generate(
  libsnutil,
  subdirs : 'esnet-smartnic',
)

libsnutil_dep = declare_dependency(
  include_directories : [ext_incdir],
  link_with : [
    libsnutil
  ])
