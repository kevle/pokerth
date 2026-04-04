cmake_minimum_required(VERSION 3.15)
project(libb2 C)

# Pure reference implementations only — no SIMD, safe for any target including wasm.
# Target named "b2" so cmake produces "libb2.a" (lib<name>.a), matching the
# autoconf build and the NAMES hint in Qt's FindLibb2.cmake.
add_library(b2
    src/blake2b-ref.c
    src/blake2s-ref.c
    src/blake2bp.c
    src/blake2sp.c
)

# Compile the ref files with -DSUFFIX= (empty) so that the token-paste macro
# BLAKE2_IMPL_NAME(fun) expands to e.g. blake2b_init (public name).
# This matches how the autoconf build compiles libb2_la when no SIMD is present.
set_source_files_properties(
    src/blake2b-ref.c src/blake2s-ref.c
    PROPERTIES COMPILE_DEFINITIONS "SUFFIX="
)

target_include_directories(b2 PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:include>
)

# Install library and header
include(GNUInstallDirs)
install(TARGETS b2
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES src/blake2.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

# Generate a pkg-config file so Qt can find libb2 via pkg_check_modules("libb2")
set(prefix "${CMAKE_INSTALL_PREFIX}")
set(libdir "\${prefix}/${CMAKE_INSTALL_LIBDIR}")
set(includedir "\${prefix}/${CMAKE_INSTALL_INCLUDEDIR}")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/libb2.pc.in"
    "${CMAKE_CURRENT_BINARY_DIR}/libb2.pc"
    @ONLY
)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/libb2.pc"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig
)
