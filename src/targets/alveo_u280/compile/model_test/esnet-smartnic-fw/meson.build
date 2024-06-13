project(
  'esnet-smartnic',
  ['c', 'cpp'],
  default_options : [
    'warning_level=2',
    'werror=true',
  ],
)

meson.override_find_program('regio-generate', find_program('regio/regio-generate'))
meson.override_find_program('regio-elaborate', find_program('regio/regio-elaborate'))
meson.override_find_program('regio-info', find_program('regio/regio-info'))

install_data(
  [
    find_program('regio/regio').full_path(),
    find_program('regio/regio-elaborate').full_path(),
    find_program('regio/regio-generate').full_path(),
    find_program('regio/regio-info').full_path(),
  ],
  install_dir : 'bin',
  install_mode : 'rwxr-xr-x',
)

subproject('gtest')
subproject('cli11')

subproject('esnet-smartnic-hwapi', default_options: ['default_library=static'])
subdir('libsnutil')
subdir('libsnp4')
subdir('libopennic')
subdir('sn-p4-proto')
subdir('sn-p4-agent')
subdir('sn-p4-cli')
subdir('sn-cli')
