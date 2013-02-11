import json, time
import numpy as np
import serialize


def test_serialize_stream_config():
  sc = serialize.StreamConfig('C3 Cz C4'.split(), 128., 'Biosemi')
  payload = sc.tostring()
  assert isinstance(payload, str)
  assert serialize.StreamConfig.fromstring(payload) == sc


def test_serialize_annotations():
  a = serialize.Annotation(
    annotator='John', text='STUNNED?', local_time=10, server_time=10.02,
    duration=2.3, offset=-.1)

  payload = a.tostring()
  assert isinstance(payload, str)
  serialize.Annotation.fromstring(payload) == a


def test_serialize_samples():
  n, p = 10, 16
  s = serialize.Samples(
    np.arange(n * p).reshape(n, -1).astype(np.float32) * .1,
    local_time=time.time())

  payload = s.tostring()

  # Test if the representation is not too inefficient; in compressed
  # form it should *improve* upon the raw binary form:
  assert len(payload.encode('zip')) < s.samples.nbytes

  assert isinstance(payload, str)
  serialize.Samples.fromstring(payload) == s
