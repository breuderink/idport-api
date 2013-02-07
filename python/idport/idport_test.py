import mock
import requests
import idport

def test_post_stream():
  '''Test the intended code path for posting a stream.'''
  with mock.patch('requests.post') as rpost:
    # Create a mocked response object.
    response = mock.MagicMock()
    response.raise_for_status = mock.MagicMock()
    response.json = mock.MagicMock(return_value=dict(stream_id='test_stream'))

    # Make request.post return the response object.
    rpost.return_value = response

    # Do the actual call.
    labels, fs, hw_id = ['a', 'b', 'c'], 64, 'test_hw'
    stream_id = idport.post_stream(
      'http://example.com', 'test-user', labels, fs, hw_id)

    # Verify calls and result.
    rpost.assert_called_with('http://example.com/u/test-user/s', 
      data='{"hardware_id": "test_hw", "sample_rate": 64.0, ' +
        '"sensor_labels": ["a", "b", "c"]}')

    assert stream_id == 'test_stream'
