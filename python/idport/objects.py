import json, math
import numpy as np

class StreamConfig:
  def __init__(self, sensor_labels=[], sample_rate=0., hardware_id=''):
    self.sensor_labels = list(sensor_labels)
    self.sample_rate = float(sample_rate)
    self.hardware_id = str(hardware_id)


  @classmethod
  def fromstring(cls, s):
    d = json.loads(s)
    sensor_labels = d['sensor_labels']
    sample_rate = d['sample_rate']
    hardware_id = d.get('hardware_id', 'undefined')
    return cls(sensor_labels, sample_rate, hardware_id)


  def tostring(self):
    config = dict(  
      sensor_labels=[str(l) for l in self.sensor_labels], 
      sample_rate=float(self.sample_rate),
      hardware_id=str(self.hardware_id))
    return json.dumps(config, sort_keys=True)


  def __eq__(self, other):
    return (
      self.sensor_labels == other.sensor_labels and
      self.sample_rate == other.sample_rate and
      self.hardware_id == other.hardware_id)


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



class Samples:
  def __init__(self, samples, local_time=None, server_time=None):
    self.samples = np.asarray(samples, np.float32)
    self.local_time = float(local_time) if local_time else None
    self.server_time = float(server_time) if server_time else None


  @classmethod
  def fromstring(cls, s):
    d = json.loads(s)
    samples = np.asarray([deserialize_singles(samp) for samp in d['samples']])
    ltime = d.get('local_time')
    stime = d.get('server_time')
    return cls(samples, ltime, stime)

  
  def tostring(self):
    d = dict(samples=[serialize_singles(s) for s in self.samples])
    if self.local_time:
      d['local_time'] = self.local_time
    if self.server_time:
      d['server_time'] = self.server_time

    return json.dumps(d, indent=2, sort_keys=True)


  def __eq__(self, other):
    return (
      np.array_equal(self.samples, other.samples) and
      self.local_time == other.local_time and
      self.server_time == other.server_time)


class Annotation:
  def __init__(self, annotator='', text='', local_time=None,
    server_time=None, duration=0., offset=0.):
    self.annotator = str(annotator)
    self.text = str(text)
    self.local_time = float(local_time)
    self.server_time = float(server_time) if server_time else None
    self.duration = float(duration)
    self.offset = float(offset)
    
    assert duration >= 0.


  @classmethod
  def fromstring(cls, s):
    d = json.loads(s)
    return cls(
      annotator=d.get('annotator'),
      text=d.get('text', ''),
      local_time=d.get('local_time', 'nan'),
      server_time=d.get('server_time', 'nan'),
      duration=d.get('duration', 0),
      offset=d.get('offset', 0))


  def tostring(self):
    d = dict(annotator=self.annotator, text=self.text,
      local_time=self.local_time, duration=self.duration,
      offset=self.offset)

    if self.server_time:
      d['server_time'] = self.server_time

    return json.dumps(d, indent=2, sort_keys=True)


  def __eq__(self, other):
    return (
      self.annotator == other.annotator and
      self.text == other.text and
      self.local_time == other.local_time and
      self.server_time == other.server_time and
      self.duration == other.duration and
      self.offset == other.offset)


class Detections:
  def __init__(self, prob_dict):
    self.probabilities = dict(prob_dict)
    assert all([0. <= v <= 1. for v in self.probabilities.values()])


  @classmethod
  def fromstring(cls, s):
    d = json.loads(s)
    return cls(d.get('detection', {}))


  def tostring(self):
    return json.dumps(dict(detection=self.probabilities))


  def __eq__(self, other):
    return (self.probabilities == other.probabilities)
