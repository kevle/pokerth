# Wrapper around the Emscripten toolchain.
# The Emscripten platform module sets ENV{PKG_CONFIG_LIBDIR} to its own sysroot
# pkgconfig directories, which prevents vcpkg host packages (built for x64-linux)
# from finding system libraries via pkg-config. We include the real toolchain
# first and then unset that variable so all host-triplet cmake subprocesses
# (launched by vcpkg portfiles) inherit a clean pkg-config search environment.
include("$ENV{EMSDK}/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake")
unset(ENV{PKG_CONFIG_LIBDIR})

# vcpkg's linux.cmake toolchain maps VCPKG_C_FLAGS → CMAKE_C_FLAGS_INIT, but
# for Emscripten we use a chainload toolchain, bypassing that mapping.
# Mirror linux.cmake's behaviour so triplet flags (e.g. -matomics -mbulk-memory)
# actually reach the compiler invocations for every vcpkg package build.
if(DEFINED VCPKG_C_FLAGS)
    string(APPEND CMAKE_C_FLAGS_INIT " ${VCPKG_C_FLAGS}")
    string(APPEND CMAKE_ASM_FLAGS_INIT " ${VCPKG_C_FLAGS}")
endif()
if(DEFINED VCPKG_CXX_FLAGS)
    string(APPEND CMAKE_CXX_FLAGS_INIT " ${VCPKG_CXX_FLAGS}")
endif()
