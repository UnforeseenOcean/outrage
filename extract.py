import json
import sys
import numpy as np
import subprocess
import os
import glob

paths = sys.argv[1:]

for path in paths:
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print e
        continue

    events = data['events']
    vid = data['file']

    if len(glob.glob('frames/' + os.path.basename(vid) + '.*')) > 0:
        print 'skipping', vid
        continue

    else:
        print 'extracting', vid

    faces = [e for e in events if len(e['faces']) > 0]

    eyediffs = [(e['eyediff'], e['frame'], e['time']) for e in events if e['eyediff'] > 0 and e['eyediff'] < 20]
    eyediffvals = [e[0] for e in eyediffs]
    if len(eyediffs) == 0:
        continue

    mean  = np.mean(eyediffvals)
    stddev = np.std(eyediffvals)
    max_val = max(eyediffvals)

    # eyediffs = [e for e in eyediffs if abs(e[0]-mean) > stddev and e[0] > mean]
    eyediffs = [e for e in eyediffs if (e[0]/max_val)>=.9]
    for ed, f, t in eyediffs:
        out = 'frames/' + os.path.basename(vid) + '.' + str(t) + '.jpg'
        args = ['ffmpeg', '-n', '-ss', str(t/1000.0), '-i', vid, '-frames:v', '1', out]
        print vid, ed, t, out
        subprocess.call(args)
