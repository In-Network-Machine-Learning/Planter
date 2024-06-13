cpp = meson.get_compiler('cpp')

libgrpcpp = dependency('grpc++')
libprotobuf = dependency('protobuf')

protoc = find_program('protoc')
grpc_cpp_plugin = find_program('grpc_cpp_plugin')

protoc_gen = generator(
  protoc,
  output : [
    '@BASENAME@.grpc.pb.cc',
    '@BASENAME@.grpc.pb.h',
    '@BASENAME@.pb.cc',
    '@BASENAME@.pb.h',
  ],
  arguments : [
    '--proto_path=@CURRENT_SOURCE_DIR@',
    '--cpp_out=@BUILD_DIR@',
    '--grpc_out=@BUILD_DIR@',
    '--plugin=protoc-gen-grpc=@0@'.format(grpc_cpp_plugin.path()),
    '@INPUT@',
  ]
)

sn_p4_v1_proto = declare_dependency(
  sources : protoc_gen.process('sn_p4_v1.proto'),
  dependencies : [
    libgrpcpp,
    libprotobuf,
  ],
)

