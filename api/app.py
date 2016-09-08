#!/usr/bin/env python3
import connexion
import datetime
import json
import logging
import os
import random
import smtplib
import string

from connexion import NoContent
from email.mime.text import MIMEText

DATA_PATH = os.getenv('DATA_PATH', 'data')

logger = logging.getLogger('api')


def random_id(prefix: str, length: int):
    return prefix + ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(length))


def send_confirmation_mail(job: dict, job_id: str, token: str):
    text = '''
Follow this link to confirm your job posting:
https://freesoftwarejobs.org/confirm/{}/{}
'''.format(job_id, token)

    msg = MIMEText(text)
    msg['Subject'] = 'Please confirm your job posting'
    msg['From'] = 'no-reply@freesoftwarejobs.org'
    msg['To'] = job['created_by']

    logger.info('Sending confirmation mail for %s to %s..', job_id, msg['To'])
    server = smtplib.SMTP('localhost')
    server.send_message(msg)
    server.quit()



def get_jobs(limit):
    return NoContent, 501


def get_job(job_id):
    return NoContent, 501


def post_job(job: dict):
    # no way to properly validate email addresses, so let's keep it simple..
    if '@' not in job.get('created_by', ''):
        return 'Invalid email', 400

    job_id = random_id('job-', 16)
    token = random_id('', 20)

    job['id'] = job_id
    job['created'] = datetime.datetime.utcnow().isoformat()

    with open(os.path.join(DATA_PATH, 'tokens', token + '.json'), 'w') as fd:
        json.dump({'job_id': job_id}, fd)

    with open(os.path.join(DATA_PATH, 'jobs', '.' + job_id + '.pending.json'), 'w') as fd:
        json.dump(job, fd)

    send_confirmation_mail(job, job_id, token)

    return job_id, 201


def confirm_job(job_id, token):
    token_path = os.path.join(DATA_PATH, 'tokens', token + '.json')
    try:
        with open(token_path) as fd:
            token_data = json.load(fd)
        if token_data['job_id'] != job_id:
            raise Exception('Invalid token')
    except:
        return 'Invalid token', 400

    try:
        os.rename(os.path.join(DATA_PATH, 'jobs', '.' + job_id + '.pending.json'), os.path.join(DATA_PATH, 'jobs', job_id + '.json'))
    except FileNotFoundError:
        return 'Invalid token', 400

    os.unlink(token_path)

    return 'Job {} was confirmed.'.format(job_id)


def put_job(job_id, job):
    return NoContent, 501


def delete_job(job_id):
    return NoContent, 501


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api('swagger.yaml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')
