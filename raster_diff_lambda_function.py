from __future__ import print_function

import os
import subprocess
import json

# Relative path to precompiled libraries/binaries
libdir = os.path.join(os.getcwd(), 'local', 'lib')
bindir = os.path.join(os.getcwd(), 'local', 'bin')

def handler(event, context):
    # Set a local library path and run main worker
    command = 'LD_LIBRARY_PATH={} PATH=$PATH:{} ./raster_diff {} {}'.format(
        libdir, bindir)

    output = subprocess.check_output(command, shell=True)
    print(output)
    return json.dumps(output)
