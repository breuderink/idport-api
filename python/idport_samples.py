import logging, argparse, json
import numpy as np
import requests

log = logging.getLogger(__name__)


def post_header(url, user, sensor_labels, sample_rate, hardware_id):
  config = dict(sensor_labels=sensor_labels, sample_rate=sample_rate,
    hardware_id=hardware_id)
  r = requests.post('%(url)s/u/%(user)s/s' % dict(url=url, user=user), 
    data=json.dumps(config))
  r.raise_for_status()  # Raise exception on error.

  d = r.json
  return d['stream_id']


def serialize_singles(sample):
  '''Convert a single single precision sample to a JSON compatible string.'''
  return np.asarray(sample).astype('<f4').tostring().encode('base64')


def deserialize_singles(string):
  return np.fromstring(string.decode('base64'), '<f4')


def serialize_samples(samples, local_time):
  return json.dumps(dict(
    samples=[serialize_singles(s) for s in samples],
    local_time=local_time))


def post_samples(url, stream_id, samp):
  payload = serialize_samples(samp, time.time())
  log.debug(payload)
  r = requests.post(url, data=payload)
  r.raise_for_status()  # Raise exception on error.
