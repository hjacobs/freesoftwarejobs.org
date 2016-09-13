#!/usr/bin/env python3

import hashlib
import jinja2
import json
import os
import re
import struct
import subprocess

os.makedirs('output/jobs', exist_ok=True)
subprocess.check_call('cp -r files/* output/', shell=True)

data_path = os.getenv('DATA_PATH', 'api/data')
jobs_path = os.path.join(data_path, 'jobs')

jobs = {}

for entry in os.listdir(jobs_path):
    if entry.startswith('job-') and entry.endswith('.json'):
        with open(os.path.join(jobs_path, entry)) as fd:
            data = json.load(fd)
        h = hashlib.new('sha1')
        h.update(data['id'].encode('ascii'))
        prefix = '{}-'.format(struct.unpack('i', h.digest()[:4])[0] % 10000)
        data['slug'] = prefix + re.sub('[^a-z0-9-]', '-', data['title'].lower() + ' ' + data['employer'].lower())
        jobs[data['id']] = data

loader = jinja2.FileSystemLoader('templates')
env = jinja2.Environment(loader=loader)
for tpl in os.listdir('templates'):
    if tpl.endswith('.html') and tpl != 'job.html':
        template = env.get_template(tpl)
        template.stream(jobs=jobs).dump('output/' + tpl)

for job in jobs.values():
    template = env.get_template('job.html')
    template.stream(job=job).dump(os.path.join('output/jobs', job['slug'] + '.html'))
