import json
import numpy as np
import mock
import requests
import idport, serialize

def test_post_stream():
  '''Test the intended (nice) code path for posting a stream.'''
  with mock.patch('requests.post') as mock_post:
    # Create a mocked response object.
    mock_r = mock.create_autospec(requests.Response)
    mock_r.json = mock.MagicMock(return_value=dict(stream_id='test_stream'))

    # Make request.post return the response object.
    mock_post.return_value = mock_r

    # Do the actual call.
    labels, fs, hw_id = ['a', 'b', 'c'], 64, 'test_hw'
    stream_id = idport.post_stream(
      'http://example.com', 'test-user', labels, fs, hw_id)

    # Verify URL and data posted to URL.
    (url,), kwargs = mock_post.call_args
    assert url == 'http://example.com/u/test-user/s'
    assert json.loads(kwargs['data']) == json.loads(json.dumps(
      dict(hardware_id=hw_id, sample_rate=fs, sensor_labels=labels)))

    # Check that errors are raised.
    mock_r.raise_for_status.assert_called_with()

    assert stream_id == 'test_stream'


def test_post_samples():
  with mock.patch('requests.post') as mock_post:
    # Create a mocked response object.
    mock_r = mock.create_autospec(requests.Response)
    mock_r.json = mock.MagicMock(return_value=dict(stream_id='test_stream'))

    # Make request.post return the response object.
    mock_post.return_value = mock_r

    # Do the actual call.
    t, S = 123.4, np.random.randn(2, 6)
    stream_id = idport.post_samples(
      'http://example.com', 'test-user', 'test-stream', S, local_time=t)

    # Verify URL and data posted to URL.
    (url,), kwargs = mock_post.call_args
    assert url == 'http://example.com/u/test-user/s/test-stream/samples'
    assert kwargs['data'] == serialize.serialize_samples(S, local_time=t)

    # Check that errors are raised.
    mock_r.raise_for_status.assert_called_with()