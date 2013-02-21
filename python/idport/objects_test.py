import json, time
import numpy as np
from objects import *


def test_serialize_stream_config():
  payload = '''
  {
    "description": "", 
    "hardware_id": "Biosemi", 
    "sample_rate": 128.0, 
    "sensor_labels": [
      "C3", 
      "Cz", 
      "C4"
    ]
  }
  '''
  sc = StreamConfig('C3 Cz C4'.split(), 128., 'Biosemi')
  assert StreamConfig.fromstring(payload) == sc


def test_serialize_annotations():
  a = Annotation(
    annotator='John', text='STUNNED?', local_time=10, server_time=10.02,
    duration=2.3, offset=-.1)

  payload = a.tostring()
  assert isinstance(payload, str)
  Annotation.fromstring(payload) == a


def test_serialize_samples():
  n, p = 10, 16
  s = Samples(
    np.arange(n * p).reshape(n, -1).astype(np.float32) * .1,
    local_time=time.time())

  payload = s.tostring()

  # Test if the representation is not too inefficient; in compressed
  # form it should *improve* upon the raw binary form:
  assert len(payload.encode('zip')) < s.samples.nbytes

  assert isinstance(payload, str)
  Samples.fromstring(payload) == s


def test_serialize_detections():
  d = Detections(dict(a=0.1, b=0.3))
  payload = d.tostring()
  assert isinstance(payload, str)
  assert Detections.fromstring(payload) == d
