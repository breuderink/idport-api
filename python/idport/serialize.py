import json
import numpy as np


def serialize_stream_config(sensor_labels, sample_rate, hardware_id):
  '''Encode streaming configuration in JSON.'''
  config = dict(  
    sensor_labels=[str(l) for l in sensor_labels], 
    sample_rate=float(sample_rate),
    hardware_id=str(hardware_id))
  return json.dumps(config)


def deserialize_stream_config(string):
  d = json.loads(string)
  sensor_labels = d['sensor_labels']
  sample_rate = float(d['sample_rate'])
  hardware_id = d.get('hardware_id', 'undefined')
  return sensor_labels, sample_rate, hardware_id


def serialize_singles(sample):
  r'''
  Convert a single single precision sample to a JSON compatible string.
  This is done by first converting the single precision floats to a
  4-byte little-endian format, and subsequently Base64 encoding the
  resulting byte array. Note that this adds a small overhead of 33%, but
  this is convenient for JSON encoding.

  Example
  -------
  >>> serialize_singles([0, 1, 2, np.pi])
  'AAAAAAAAgD8AAABA2w9JQA==\n'

  '''
  return np.asarray(sample).astype('<f4').tostring().encode('base64')


def deserialize_singles(string):
  r'''
  Example
  -------
  >>> deserialize_singles('AAAAAAAAgD8AAABA2w9JQA==\n')
  ... # doctest: +NORMALIZE_WHITESPACE
  array([ 0. ,  1. ,  2. , 3.14159274], dtype=float32)
  '''
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


def deserialize_samples(s):
  r'''
  Deserialize samples from JSON format.

  Returns
  -------
  samples : NumPy array with shape (n, p)
    Two dimensional array with n samples from p sensors, stored in
    single precision floating point format.
  local_time : float
    Client timestamp of moment that the samples were recorded.
  server_time : float
    Server timestamp of moment that the samples were received.

  Example
  -------
  First we serialize some samples:
  >>> S0 = [[0, 1, 2, 3], [1, 1, 2, 3]]
  >>> payload = serialize_samples(S0, 123.)
  >>> type(payload)
  <type 'str'>
    
  Now, we can extract the information again:
  >>> S, ltime, stime = deserialize_samples(payload)
  >>> S
  array([[ 0.,  1.,  2.,  3.],
         [ 1.,  1.,  2.,  3.]], dtype=float32)
  >>> ltime
  123.0
  >>> stime
  nan
  '''
  d = json.loads(s)
  samples = np.asarray([deserialize_singles(samp) for samp in d['samples']])
  ltime = float(d.get('local_time', 'nan'))
  stime = float(d.get('server_time', 'nan'))

  return samples, ltime, stime
