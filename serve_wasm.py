#!/usr/bin/env python3
"""
Simple HTTP server for WebAssembly debugging.
Serves build/emsdk-debug/bin with the headers required for SharedArrayBuffer
(Cross-Origin-Opener-Policy, Cross-Origin-Embedder-Policy) and correct MIME types.

Additional "include paths" can be mounted at URL prefixes so that browser
devtools can resolve DWARF source references or other assets that live
outside the main bin directory.

Usage:
    python serve_wasm.py [--port PORT] [--host HOST] [--include PREFIX=PATH ...]

Examples:
    python serve_wasm.py
    python serve_wasm.py --port 8080
    python serve_wasm.py --include /src=/workspaces/pokerth/src
    python serve_wasm.py --include /src=src --include /third_party=third_party
"""

import argparse
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

SERVE_DIR = Path(__file__).parent / "build" / "emsdk-debug" / "bin"

EXTRA_MIME_TYPES = {
    ".wasm": "application/wasm",
    ".js":   "application/javascript",
    ".mjs":  "application/javascript",
    ".map":  "application/json",
    ".svg":  "image/svg+xml",
}

WASM_HEADERS = {
    "Cross-Origin-Opener-Policy":   "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cache-Control":                "no-cache",
}


def make_handler(base_dir: Path, include_paths: dict[str, Path]):
    """Return a request-handler class configured for the given directories."""

    class WasmHandler(SimpleHTTPRequestHandler):
        def translate_path(self, path: str) -> str:
            # Strip query string / fragment
            url_path = urlparse(path).path

            # Check include paths first (longest prefix wins)
            for prefix, mapped_dir in sorted(
                include_paths.items(), key=lambda kv: -len(kv[0])
            ):
                if url_path.startswith(prefix):
                    relative = url_path[len(prefix):].lstrip("/")
                    return str(mapped_dir / relative)

            # Fall back to the main serve directory
            relative = url_path.lstrip("/")
            return str(base_dir / relative)

        def end_headers(self):
            for name, value in WASM_HEADERS.items():
                self.send_header(name, value)
            # Emit SourceMap: header for .wasm files so DevTools picks up the
            # source map even if it ignores the sourceMappingURL custom section.
            if Path(self.path.split("?")[0]).suffix.lower() == ".wasm":
                wasm_name = Path(self.path.split("?")[0]).name
                self.send_header("SourceMap", f"http://localhost:{self.server.server_address[1]}/{wasm_name}.map")
            super().end_headers()

        def guess_type(self, path: str):
            ext = Path(path).suffix.lower()
            if ext in EXTRA_MIME_TYPES:
                return EXTRA_MIME_TYPES[ext]
            return super().guess_type(path)

        def log_message(self, fmt, *args):
            # Colour-code by status code for readability
            msg = fmt % args
            code = args[1] if len(args) > 1 else ""
            if str(code).startswith("2"):
                colour = "\033[32m"   # green
            elif str(code).startswith("3"):
                colour = "\033[33m"   # yellow
            elif str(code).startswith(("4", "5")):
                colour = "\033[31m"   # red
            else:
                colour = ""
            reset = "\033[0m" if colour else ""
            print(f"{colour}{self.log_date_time_string()}  {msg}{reset}")

    return WasmHandler


def parse_include(value: str) -> tuple[str, Path]:
    """Parse a PREFIX=PATH string into (url_prefix, filesystem_path)."""
    if "=" not in value:
        sys.exit(f"--include must be in PREFIX=PATH format, got: {value!r}")
    prefix, _, path_str = value.partition("=")
    if not prefix.startswith("/"):
        prefix = "/" + prefix
    resolved = Path(path_str).resolve()
    if not resolved.exists():
        sys.exit(f"Include path does not exist: {resolved}")
    return prefix, resolved


def main():
    parser = argparse.ArgumentParser(
        description="WASM-ready HTTP server for pokerth emsdk builds."
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument(
        "--serve-dir",
        default=str(SERVE_DIR),
        metavar="DIR",
        help=f"Directory to serve (default: {SERVE_DIR})",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=["/opt/=/opt","/=/workspaces/pokerth/build/emsdk-debug/bin","/src=/workspaces/pokerth/src","/emsdk=/opt/emsdk","/vcpkg_installed=/workspaces/pokerth/build/emsdk-debug/vcpkg_installed","/.well-known=/workspaces/pokerth/.well-known"],
        metavar="PREFIX=PATH",
        help=(
            "Mount an extra directory at a URL prefix, e.g. "
            "--include /src=src  "
            "Can be repeated."
        ),
    )
    args = parser.parse_args()

    base_dir = Path(args.serve_dir).resolve()
    if not base_dir.exists():
        sys.exit(f"Serve directory does not exist: {base_dir}")

    include_paths: dict[str, Path] = {}
    for raw in args.include:
        prefix, path = parse_include(raw)
        include_paths[prefix] = path

    handler = make_handler(base_dir, include_paths)
    server = HTTPServer((args.host, args.port), handler)

    print(f"Serving  {base_dir}")
    for prefix, path in include_paths.items():
        print(f"  {prefix}  →  {path}")
    print(f"Listening on  http://{args.host}:{args.port}/")
    print("Headers:")
    for k, v in WASM_HEADERS.items():
        print(f"  {k}: {v}")
    print("Press Ctrl-C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
