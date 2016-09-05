#!/usr/bin/env python3
import connexion
import datetime
import logging

from connexion import NoContent

# our memory-only job storage
jobS = {}


def get_jobs(limit):
    pass


def get_job(job_id):
    job = jobS.get(job_id)
    return job or ('Not found', 404)


def post_job():
    pass


def put_job(job_id, job):
    exists = job_id in jobS
    job['id'] = job_id
    if exists:
        logging.info('Updating job %s..', job_id)
    else:
        logging.info('Creating job %s..', job_id)
        job['created'] = datetime.datetime.utcnow()
    jobS[job_id] = job
    return NoContent, (200 if exists else 201)


def delete_job(job_id):
    if job_id in jobS:
        logging.info('Deleting job %s..', job_id)
        del jobS[job_id]
        return NoContent, 204
    else:
        return NoContent, 404


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api('swagger.yaml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')
