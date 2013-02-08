import json, time
import numpy as np
import serialize


def test_serialize_stream_config():
  labels = ['Sensor %d' % i for i in range(10)]
  fs = 1024.
  hw_id = 'blah'

  payload = serialize.serialize_stream_config(labels, fs, hw_id)
  assert isinstance(payload, str)
  labels2, fs2, hw_id = serialize.deserialize_stream_config(payload)

  assert labels2 == labels
  assert fs2 == fs
  assert hw_id == hw_id


def test_serialize_samples():
  n, p = 10, 14  # n samples from p sensors.

  ltime = time.time()
  S = np.arange(n * p).reshape(n, -1).astype(np.float32) * .1
  print S

  r = serialize.serialize_samples(S, ltime)
  print r
  d = json.loads(r)

  # Check global properties.
  assert d['local_time'] == ltime
  assert len(d['samples']) == n

  # Check that samples can be transformed back.
  for si, samp in enumerate(d['samples']):
    np.testing.assert_allclose(
      serialize.deserialize_singles(samp[:-1]),
      S[si])

  
  # Test if the representation is not too inefficient; in compressed
  # form it should *improve* upon the raw binary form:
  assert len(r.encode('zip')) < n * p * 4
