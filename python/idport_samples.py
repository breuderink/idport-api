import logging, argparse, json
import numpy as np
import requests

import serialize

log = logging.getLogger(__name__)


def post_header(url, user, sensor_labels, sample_rate, hardware_id):
  config = dict(sensor_labels=sensor_labels, sample_rate=sample_rate,
    hardware_id=hardware_id)
  r = requests.post('%(url)s/u/%(user)s/s' % dict(url=url, user=user), 
    data=json.dumps(config))
  r.raise_for_status()  # Raise exception on error.

  d = r.json
  return d['stream_id']


def post_samples(url, stream_id, samp):
  payload = serialize.serialize_samples(samp, time.time())
  log.debug(payload)
  r = requests.post(url, data=payload)
  r.raise_for_status()  # Raise exception on error.
