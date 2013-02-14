import json
import numpy as np
import mock
import requests
import idport
from objects import StreamConfig, Samples


@mock.patch('requests.post', autospec=True)
def test_post_stream(mock_post):
  # Create a mocked response object.
  mock_r = mock.create_autospec(requests.Response)
  mock_r.json = mock.MagicMock(return_value=dict(stream_id='test_stream'))
  mock_post.return_value = mock_r

  # Do the actual call.
  stream_cfg = StreamConfig(['a', 'b', 'c'], 64, 'test_hw')
  stream_id = idport.post_stream('http://example.com', 'test-user', stream_cfg)

  # Verify URL and data posted to URL.
  (url,), kwargs = mock_post.call_args
  assert url == 'http://example.com/u/test-user/s'
  assert StreamConfig.fromstring(kwargs['data']) == stream_cfg

  # Check that errors are raised.
  mock_r.raise_for_status.assert_called_with()
  assert stream_id == 'test_stream'


@mock.patch('requests.post', autospec=True)
def test_post_samples(mock_post):
  # Create a mocked response object.
  mock_r = mock.create_autospec(requests.Response)
  mock_r.json = mock.MagicMock(return_value=dict(stream_id='test_stream'))
  mock_post.return_value = mock_r

  # Do the actual call.
  samp = Samples(np.random.randn(2, 6), 123.4)
  stream_id = idport.post_samples(
    'http://example.com', 'test-user', 'test-stream', samp)

  # Verify URL and data posted to URL.
  (url,), kwargs = mock_post.call_args
  assert url == 'http://example.com/u/test-user/s/test-stream/samples'
  assert kwargs['data'] == samp.tostring()

  # Check that errors are raised.
  mock_r.raise_for_status.assert_called_with()
