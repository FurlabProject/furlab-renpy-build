from renpybuild.context import Context
from renpybuild.task import task
import os
import subprocess
import re

EXPORT = "{{ root }}/renpy-ios-runtime"

# ---------------------------------------------------------
# Verify SDK metadata
# ---------------------------------------------------------

def check_sdk(name, paths):

    for d in paths:
        fn = d / name

        p = subprocess.run(
            ["llvm-otool-15", "-l", f"{fn}"],
            capture_output=True
        )

        obj = None

        for l in p.stdout.decode("utf-8").split("\n"):

            if re.match(r'.*\.a\(.*\)', l):
                if obj is not None and not ("asm" in obj):
                    raise Exception(f"{obj} does not have a minos defined, in {fn}")
                obj = l

            if "minos" in l:
                obj = None


# ---------------------------------------------------------
# Copy static libraries per platform
# ---------------------------------------------------------

def copy_libs(c: Context, src, dst, namefilter):

    c.run(f"install -d {dst}")

    for i in src.glob("*.a"):

        if i.is_symlink():
            continue

        name = i.name

        if not namefilter(name):
            continue

        check_sdk(name, [src])

        print(f"(Copy) {src}/{name} → {c.expand(dst)}/{name}")

        c.run(f"cp {src}/{name} {dst}/{name}")
        os.chmod(c.path(f"{dst}/{name}"), 0o755)

    print("ROOT:", c.expand("{{ root }}"))
    print("TMP:", c.expand("{{ tmp }}"))
    print("RENIOS:", c.expand("{{ renios }}"))

def ensure_export_root(c: Context):
    c.run(f"install -d {EXPORT}")

def build_platform_libs(c: Context, namefilter):

    ensure_export_root(c)

    copy_libs(
        c,
        c.path("{{ tmp }}/install.ios-arm64/lib"),
        f"{EXPORT}/ios-arm64",
        namefilter
    )

    copy_libs(
        c,
        c.path("{{ tmp }}/install.ios-sim-arm64/lib"),
        f"{EXPORT}/ios-simulator-arm64",
        namefilter
    )


# ---------------------------------------------------------
# Copy headers
# ---------------------------------------------------------

@task(kind="host-python", platforms="ios", always=True)
def copy_headers(c: Context):

    src = "{{ tmp }}/install.ios-arm64/include"
    dst = f"{EXPORT}/include"

    print("Copying headers")

    if c.path(src).exists():
        c.clean(dst)
        c.copytree(src, dst)


# ---------------------------------------------------------
# Merge libraries into libRenpyRuntime.a
# ---------------------------------------------------------

def build_runtime_lib(c: Context, platform_dir):

    src = c.path(f"{EXPORT}/{platform_dir}")
    out = src / "libRenpyRuntime.a"

    if out.exists():
        out.unlink()

    libs = [str(i) for i in src.glob("*.a") if i.name != "libRenpyRuntime.a"]

    if not libs:
        print(f"No libraries found for {platform_dir}, skipping")
        return

    print(f"Merging {len(libs)} libraries for {platform_dir}")

    cmd = ["llvm-ar", "rc", str(out)] + libs
    subprocess.run(cmd, check=True)

    subprocess.run(["llvm-ranlib", str(out)], check=True)


@task(kind="host-python", platforms="ios", always=True)
def build_runtime(c: Context):

    build_runtime_lib(c, "ios-arm64")
    build_runtime_lib(c, "ios-simulator-arm64")


# ---------------------------------------------------------
# Build XCFramework
# ---------------------------------------------------------

import platform

@task(kind="host-python", platforms="ios", always=True)
def build_xcframework(c: Context):

    if platform.system() != "Darwin":
        print("Skipping XCFramework creation (not running on macOS)")
        return

    base = c.path(EXPORT)

    ios = base / "ios-arm64/libRenpyRuntime.a"
    sim = base / "ios-simulator-arm64/libRenpyRuntime.a"
    headers = base / "include"

    output = base / "RenpyRuntime.xcframework"

    if output.exists():
        subprocess.run(["rm", "-rf", str(output)], check=True)

    subprocess.run([
        "xcodebuild",
        "-create-xcframework",
        "-library", str(ios),
        "-headers", str(headers),
        "-library", str(sim),
        "-headers", str(headers),
        "-output", str(output)
    ], check=True)


# ---------------------------------------------------------
# Main build tasks
# ---------------------------------------------------------

@task(kind="host-python", platforms="ios")
def build_all(c: Context):

    python = f"libpython{c.python}."

    def namefilter(i):

        if i.startswith("libpython") and not i.startswith(python):
            return False

        return True

    build_platform_libs(c, namefilter)


@task(kind="host-python", platforms="ios", always=True)
def build_renpy(c: Context):

    build_platform_libs(c, lambda n: "librenpy" in n)


# ---------------------------------------------------------
# Unpack MetalANGLE
# ---------------------------------------------------------

@task(kind="host-python", platforms="ios", always=True)
def unpack_metalangle(c: Context):

    c.clean("{{ renios }}/prototype/Frameworks")
    c.chdir("{{ renios }}/prototype/Frameworks")

    c.run("tar xaf {{ source }}/MetalANGLE.xcframework.tar.gz")


# ---------------------------------------------------------
# Copy back to renpy tree
# ---------------------------------------------------------

@task(kind="host-python", platforms="ios", always=True, pythons="2")
def copyback(c: Context):

    c.copytree(
        "{{ renios }}/prototype/prebuilt",
        "{{ root }}/renios/prototype/prebuilt"
    )

