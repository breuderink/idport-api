import json
import numpy as np

def serialize_singles(sample):
  '''Convert a single single precision sample to a JSON compatible string.'''
  return np.asarray(sample).astype('<f4').tostring().encode('base64')


def deserialize_singles(string):
  return np.fromstring(string.decode('base64'), '<f4')


def serialize_samples(samples, local_time):
  return json.dumps(dict(
    samples=[serialize_singles(s) for s in samples],
    local_time=local_time))
