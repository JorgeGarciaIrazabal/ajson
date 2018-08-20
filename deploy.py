import ajson
import sys
from subprocess import check_call


def increment_version():
    parsed_version = ajson.__version__.split(".")
    if sys.argv[1] == "hotfix":
        index = 2
    elif sys.argv[1] == "minor":
        index = 1
    elif sys.argv[0] == "mayor":
        index = 0
    else:
        raise ValueError("argument has to be either 'hotfix', 'minor' or 'mayor'")
    parsed_version[index] = str(int(parsed_version[index]) + 1)
    version = ".".join(parsed_version)
    with open("ajson/__init__.py", "r+") as f:
        lines = list(map(lambda l: l.strip(), f.readlines()))
        for i, line in enumerate(lines):
            if line.startswith("__version__"):
                lines[i] = "__version__ = '{}'".format(version)
                break
        else:
            raise RuntimeError("unable to find function from __init__ file")
        f.seek(0)
        f.write("\n".join(lines))
    print("version updated to: {}".format(version))
    return version


if __name__ == "__main__":
    version = increment_version()
    check_call(["git", "tag", "-a", "v{}".format(version), "-m", "\"create tag: {}\"".format(version)])
    print("created tag: v{}".format(version))
    check_call(["git", "push", "origin", "--tags"])
    print("pushed tag: v{}".format(version))
