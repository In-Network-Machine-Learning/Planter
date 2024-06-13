sn_p4_agent = executable(
  'sn-p4-agent',
  files(
    [
      'src/sn-p4-agent.cpp',
    ]
  ),
  include_directories : include_directories(
    [
    ]
  ),
  dependencies : [
    libgmp_dep,
    libopennic_dep,
    libsnp4_dep,
    sn_p4_v1_proto,
    dependency('regmap'),
  ],
  install : true,
)
