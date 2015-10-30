import json
import sys
import numpy as np
import subprocess
import os
import random

# files = sys.argv[1:]
# random.shuffle(files)

# for f in files:
#     print "file '{}'".format(f)
                # print e

out = []

for f in sys.argv[1:]:
    base = os.path.basename(f)
    parts = base.split('.')
    jsonfile = '.'.join(parts[0:2]) + '.json'
    timestamp = float('.'.join(parts[-3:-1]))

    with open(jsonfile, 'r') as infile:
        data = json.load(infile)

    events = [e for e in data['events'] if e['time'] <= timestamp]
    events.reverse()

    eyepairs = []
    faces = []
    for i, e in enumerate(events):
        if len(e['eye_pairs']) > 0:
            eyepairs = e['eye_pairs'][0]
        if len(e['faces']) > 0:
            faces = e['faces'][0]

        if len(eyepairs) > 0 and len(faces) > 0:
            break

    out.append({'f': f, 'eyes': eyepairs, 'face': faces})
    print f, eyepairs
        # if e['time'] == timestamp:
                # print e

random.shuffle(out)
with open('eyepairs.json', 'w') as f:
    json.dump(out, f)
