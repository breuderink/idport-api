import logging, argparse, json, time
import numpy as np
import requests


log = logging.getLogger(__name__)

def post_stream(url, user_id, sensor_config):
  '''
  Create a new stream by posting header information for the stream.

  Returns
  -------
  stream_id : str
    An identifier for the newly created stream.
  '''
  r = requests.post('%s/u/%s/s' % (url, user_id), 
    data=sensor_config.tostring())
  r.raise_for_status()  # Raise exception on error.
  return r.json()['stream_id']


def get_stream(url, user_id, stream_id):
  raise NotImplementedError


def post_samples(url, user_id, stream_id, samples):
  r = requests.post('%s/u/%s/s/%s/samples' % (url, user_id, stream_id),
    data=samples.tostring())
  r.raise_for_status()  # Raise exception on error.


def get_samples(url, user_id, stream_id):
  raise NotImplementedError


def get_annotation(url, user_id, stream_id):
  raise NotImplementedError


def post_detection(url, user_id, stream_id, detections):
  r = requests.post('%(url)s/u/%(user_id)s/s/%(stream_id)s/detection' % 
    dict(url=url, user_id=user_id, stream_id=stream_id),
    data=detections.tostring())
  r.raise_for_status()  # Raise exception on error.


def get_detection(url, user_id, stream_id):
  r = requests.get('%(url)s/u/%(user_id)s/s/%(stream_id)s/detection' % 
    dict(url=url, user_id=user_id, stream_id=stream_id))
  r.raise_for_status()  # Raise exception on error.
  return r.json()['detection']
