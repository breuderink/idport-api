import json, time
import numpy as np
import serialize


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
  # form it should *improve* upon the raw form:
  assert len(r.encode('zip')) < n * p * 4
