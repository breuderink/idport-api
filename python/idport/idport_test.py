import mock
import requests
import idport

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
    mock_post.assert_called_with('http://example.com/u/test-user/s', 
      data='{"hardware_id": "test_hw", "sample_rate": 64.0, ' +
        '"sensor_labels": ["a", "b", "c"]}')
    # Test that errors are raised.
    mock_r.raise_for_status.assert_called_with()

    assert stream_id == 'test_stream'
