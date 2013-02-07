import numpy as np

def float32_to_string(a):
  a = np.asarray(a)
  return a.astype('<f4').tostring()


def string_to_float32(s):
  return np.fromstring(s, '<f4')
