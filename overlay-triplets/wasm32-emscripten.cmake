set(VCPKG_ENV_PASSTHROUGH_UNTRACKED EMSCRIPTEN_ROOT EMSDK PATH EMSDK_PYTHON)

if(NOT DEFINED ENV{EMSCRIPTEN_ROOT})
   find_path(EMSCRIPTEN_ROOT "emcc")
else()
   set(EMSCRIPTEN_ROOT "$ENV{EMSCRIPTEN_ROOT}")
endif()

if(NOT EMSCRIPTEN_ROOT)
   if(NOT DEFINED ENV{EMSDK})
      message(FATAL_ERROR "The emcc compiler not found in PATH")
   endif()
   set(EMSCRIPTEN_ROOT "$ENV{EMSDK}/upstream/emscripten")
endif()

if(NOT EXISTS "${EMSCRIPTEN_ROOT}/cmake/Modules/Platform/Emscripten.cmake")
   message(FATAL_ERROR "Emscripten.cmake toolchain file not found")
endif()

set(VCPKG_TARGET_ARCHITECTURE wasm32)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE static)
set(VCPKG_CMAKE_SYSTEM_NAME Emscripten)
# Use the project wrapper instead of bare Emscripten.cmake so that
# VCPKG_C_FLAGS/-CXX_FLAGS are propagated into CMAKE_C_FLAGS_INIT
# (the bare Emscripten.cmake doesn't know about VCPKG_C_FLAGS; our wrapper does).
set(VCPKG_CHAINLOAD_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/../cmake/EmscriptenWrapper.cmake")

# Qt 6 WASM uses -pthread at link time, which requires all objects to have been
# compiled with -matomics and -mbulk-memory (implied by -pthread at compile time).
# Apply these flags to every dependency built for wasm32-emscripten so that
# object files from protobuf, abseil, etc. are compatible with the shared-memory
# wasm binary produced by qt_add_executable.
# -fwasm-exceptions: native WebAssembly exception handling (required by Qt 6 WASM).
# -s SUPPORT_LONGJMP=wasm: C libraries that use setjmp/longjmp (e.g. protobuf's upb)
#   normally emit calls to emscripten_longjmp (the JS-based implementation). When
#   -fwasm-exceptions is active the linker no longer provides that symbol, so we
#   must also compile C code with SUPPORT_LONGJMP=wasm to use the WASM-native path.
set(VCPKG_C_FLAGS "-matomics -mbulk-memory -s SUPPORT_LONGJMP=wasm")
set(VCPKG_CXX_FLAGS "-matomics -mbulk-memory -fwasm-exceptions -s SUPPORT_LONGJMP=wasm")

# Qt's cross-compile debug tools write absolute host paths into target_qt.conf
# (HostPrefix / HostData pointing back into vcpkg_installed and buildtrees).
# This is expected and harmless; suppress vcpkg's post-build absolute-path check.
set(VCPKG_POLICY_SKIP_ABSOLUTE_PATHS_CHECK enabled)
