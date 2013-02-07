import json
import numpy as np

def serialize_singles(sample):
  '''
  Convert a single single precision sample to a JSON compatible string.

  
  '''
  return np.asarray(sample).astype('<f4').tostring().encode('base64')


def deserialize_singles(string):
  return np.fromstring(string.decode('base64'), '<f4')


def serialize_samples(samples, local_time, server_time=None):
  r'''
  Serialize a sequence of samples.

  Example
  -------
  >>> s1 = [0, 1, 2, 3]
  >>> s2 = [1, 1, 2, 3]
  >>> print serialize_samples([s1, s2], 123.)
  {
    "local_time": 123.0, 
    "samples": [
      "AAAAAAAAgD8AAABAAABAQA==\n", 
      "AACAPwAAgD8AAABAAABAQA==\n"
    ]
  }
  '''
  d = dict(
    samples=[serialize_singles(s) for s in samples], 
    local_time=local_time)
  if server_time:  # optionally add server time
    d['server_time'] = server_time

  return json.dumps(d, indent=2)
