set(VCPKG_TARGET_ARCHITECTURE x64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE static)

set(VCPKG_CMAKE_SYSTEM_NAME Linux)

# When this triplet is used as a host triplet during an Emscripten cross-compile,
# the Emscripten toolchain (Platform/Emscripten.cmake) has already set
# PKG_CONFIG_LIBDIR to the EMSDK sysroot's pkgconfig dirs.  That env var
# overrides pkg-config's built-in default search path and prevents it from
# finding system packages (e.g. xkbcommon-x11, xrender) in /usr/lib64/pkgconfig.
# Unset it so that host-side packages are found via the normal system paths.
unset(ENV{PKG_CONFIG_LIBDIR})
