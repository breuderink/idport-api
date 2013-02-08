import json
import numpy as np


def serialize_stream_config(sensor_labels, sample_rate, hardware_id):
  '''Encode streaming configuration in JSON.'''
  config = dict(  
    sensor_labels=[str(l) for l in sensor_labels], 
    sample_rate=float(sample_rate),
    hardware_id=str(hardware_id))
  return json.dumps(config, sort_keys=True)


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

  return json.dumps(d, indent=2, sort_keys=True)


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


def serialize_annotation(annotator, text, local_time, 
  server_time=None, duration=0., offset=0.):
  r'''
  Serialize an annotation of an event.

  Example
  -------
  >>> print serialize_annotation('me', 'hello', 10)
  {
    "annotator": "me", 
    "duration": 0.0, 
    "local_time": 10.0, 
    "offset": 0.0, 
    "text": "hello"
  }

  >>> print serialize_annotation('me', 'hello', 10, 10.02, 1, -.5)
  {
    "annotator": "me", 
    "duration": 1.0, 
    "local_time": 10.0, 
    "offset": -0.5, 
    "server_time": 10.02, 
    "text": "hello"
  }
  '''
  assert duration >= 0., 'Negative durations are not permitted!'

  d = dict(
    annotator=str(annotator),
    text=str(text),
    local_time=float(local_time),
    duration=float(duration),
    offset=float(offset))

  # Add optional fields.
  if server_time:
    d['server_time'] = float(server_time)

  return json.dumps(d, indent=2, sort_keys=True)


def deserialize_annotation(string):
  r'''
  Deserialize an annotation of an event.

  Returns
  -------
  annotator : str
    String describing the annotator for this event.
  text : str
    Description of this event.
  local_time : float
    Timestamp of generation of event. Note that this does not have to be
    the start of the event, nor the end!
  server_time : float
    Timestamp of the moment this annotation was received by the server.
  duration : float
    Duration of this event, in seconds.
  offset : float
    Offset of start of event from local_time: a negative value indicates
    that the event started /before/ the timestamp was generated.

  Example
  -------
  >>> payload = json.dumps(dict(
  ...   annotator='me',
  ...   text='hello',
  ...   local_time=10.0))
  >>> deserialize_annotation(payload)
  (u'me', u'hello', 10.0, nan, 0.0, 0.0)
  '''
  d = json.loads(string)
  annotator = d.get('annotator')
  text = d.get('text', '')
  ltime = float(d.get('local_time', 'nan'))
  stime = float(d.get('server_time', 'nan'))
  duration = float(d.get('duration', 0))
  offset = float(d.get('offset', 0))

  return annotator, text, ltime, stime, duration, offset
