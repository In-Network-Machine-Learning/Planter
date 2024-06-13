regio_generate_prog = find_program('regio-generate')
regio_info_prog = find_program('regio-info')

# Auto-discover the names of all of the blocks described within an IR definition
# This is used to precompute the names of all of the header files that will be
# generated.
#
# NOTE: This command is executed during the *configuration* phase and the results will be cached.
#       If you want to regenerate this list, you'll need to force one of the meson.build files to be out-of-date
#       by e.g. touch meson.build

regmap_info = run_command(
  regio_info_prog,
  'esnet-smartnic-top-ir.yaml',
)

regmap_blocks = regmap_info.stdout().strip().split('\n')
regmap_block_headers = []
foreach b : regmap_blocks
  message('Block: ' + b)
  regmap_block_headers += b + '_block.h'
endforeach

regmap_c_headers = custom_target(
  'regmap-c-headers',
  input : 'esnet-smartnic-top-ir.yaml',
  output : regmap_block_headers + ['esnet_smartnic_toplevel.h'],
  command : [
    regio_generate_prog,
    '--file-type', 'top',
    '--recursive',
    '--template-dir', '@SOURCE_ROOT@/regio/templates',
    '--generator', 'c',
    '--output-dir', '@OUTDIR@',
    '@INPUT@'
  ],
  install : true,
  install_dir : 'include/esnet-smartnic',
)

regmap_c_headers_dep = declare_dependency(
  sources : [regmap_c_headers],
  include_directories : include_directories('.')
)

meson.override_dependency(
  'regmap',
  regmap_c_headers_dep
)
