project('esnet-opennic-hwapi', 'c')

subdir('libvitisnetp4drv')
subdir('regmap')

install_subdir(
  'firmware',
  install_dir : 'lib/firmware/esnet-smartnic',
  strip_directory : true,
)

install_subdir(
  'regmap/spec',
  install_dir : 'share/esnet-smartnic-dev/spec',
  strip_directory : true,
)

install_data(
  [
    'regmap/esnet-smartnic-top-ir.yaml',
  ],
  install_dir : 'share/esnet-smartnic',
)

install_subdir(
  'wireshark',
  install_dir : get_option('libdir'),
)
