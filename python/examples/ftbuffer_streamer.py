import logging, argparse, json, time
import numpy as np
import ftbuffer  # This is the Python client for the FieldTrip buffer.
import idport


log = logging.getLogger(__name__)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Stream EEG to MindPlay')
  parser.add_argument('--ft-hostname', default='localhost',
    help='Hostname for the FieldTrip buffer server.')
  parser.add_argument('--ft-port', default=1972, type=int, 
    help='Port of the FieldTrip buffer server.')
  parser.add_argument('--hardware_id', default='unknown',
    help='Identifier of the hardware setup.')
  parser.add_argument('--chunk-size', default=16, type=int,
    help='Number of samples to read and send at once.')

  parser.add_argument('--idport-url', default='http://localhost:8080',
    help='URL of IDport REST API.')
  parser.add_argument('--user-id', default='test-user')
  parser.add_argument('--stream-id', default='test-stream')

  parser.add_argument('--verbose', '-v', action='store_true',
    help='Number of samples to read and send at once.')
  args = parser.parse_args()
  
  # Setup output.
  logging.basicConfig(level=logging.WARNING)
  if args.verbose:
    log.setLevel(logging.DEBUG)
  else:
    log.setLevel(logging.INFO)
  np.set_printoptions(precision=2)

  # First, we setup a connection and determine the streaming
  # configuration.
  ftc = ftbuffer.Client()   

  log.info('Connecting to FieldTrip buffer at %s:%s...', 
    args.ft_hostname, args.ft_port)
  ftc.connect(args.ft_hostname, args.ft_port)
  
  log.info('Reading EEG config.')
  H = ftc.getHeader()
  assert H
  assert H.dataType == 10  
  # Magic number from Emotiv EPOC stream... I don't know how well other
  # data types work.

  # Create a stream on the IDPort server
  stream_config = idport.StreamConfig(H.labels, H.fSample, args.hardware_id)
  stream_id = idport.post_stream(args.idport_url, args.user_id, stream_config)
  log.info('Created stream %s.', stream_id)

  # Start streaming from the /current/ point in time.
  i = H.nSamples - 1
  log.info('Starting streaming from sample %d...', i)

  while True:
    nsamples, nevents = ftc.poll()
    log.debug('Server holds %d samples and %d events.', nsamples, nevents)
    assert nevents == 0, 'Handling of events is not implemented!'

    log.debug('Waiting for new data...')
    ftc.wait(i + args.chunk_size, 0, 1000)  # TODO: check for off-by-one errors.

    # Get new samples and verify it's dimensions.
    D = ftc.getData([i, i + args.chunk_size - 1])
    log.debug(D)
    assert D != None, 'Timeout while reading samples!'
    assert D.shape[0] == args.chunk_size
    i += D.shape[0]

    # Post samples to server.
    idport.post_samples(args.idport_url, args.user_id, stream_id, 
      idport.Samples(D, time.time()))
        
    time.sleep(.01)
  
  log.info('Disconnecting from FieldTrip buffer...')
  ftc.disconnect()
