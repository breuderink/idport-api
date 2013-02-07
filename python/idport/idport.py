import logging, argparse, json
import numpy as np
import requests

import serialize

log = logging.getLogger(__name__)


def post_stream(url, user_id, sensor_labels, sample_rate, 
  hardware_id='unknown'):
  '''
  Create a new stream by posting header information for the stream.

  Returns
  -------
  stream_id : str
    An identifier for the newly created stream.
  '''
  config = dict(  
    sensor_labels=sensor_labels, 
    sample_rate=sample_rate,
    hardware_id=hardware_id)
  r = requests.post('%(url)s/u/%(user_id)s/s' % 
    dict(url=url, user_id=user_id), data=json.dumps(config))

  r.raise_for_status()  # Raise exception on error.
  return r.json()['stream_id']


def get_stream(url, user_id, stream_id):
  raise NotImplementedError


def post_samples(url, user_id, stream_id, samp):
  payload = serialize.serialize_samples(samp, time.time())
  log.debug(payload)
  r = requests.post(url, data=payload)
  r.raise_for_status()  # Raise exception on error.


def get_samples(url, user_id, stream_id):
  raise NotImplementedError


def get_annotation(url, user_id, stream_id):
  raise NotImplementedError


def get_detection(url, user_id, stream_id):
  r = requests.get('%(url)s/u/%(user_id)s/s/%(stream_id)s/detection' % 
    dict(url=url, user_id=user_id, stream_id=stream_id))
  r.raise_for_status()  # Raise exception on error.
  return r.json()['detection']
