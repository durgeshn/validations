import maya.standalone
import maya.OpenMaya as OpenMaya

import sys


def main(argv=None):
    try:
        maya.standalone.initialize(name='python')
    except:
        sys.stderr.write("Failed in initialize standalone application")
        raise

    sys.stderr.write("Hello world! (script output)\n")
    OpenMaya.MGlobal().executeCommand("print \"Hello world! (command script output)\\n\"")


if __name__ == "__main__":
    main()
