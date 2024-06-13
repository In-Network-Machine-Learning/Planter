CLI11_dep = dependency('cli11', fallback : ['cli11', 'CLI11_dep'], main : true, required : true)

sn_p4_cli = executable(
  'sn-p4-cli',
  files(
    [
      'src/sn-p4-cli.cpp',
    ]
  ),
  include_directories : include_directories(
    [
    ]
  ),
  cpp_args : [
    '-std=c++2a',
  ],
  dependencies : [
    CLI11_dep,
    libgmp_dep,
    libopennic_dep,
    libsnp4_dep,
    sn_p4_v1_proto,
  ],
  install : true,
)
