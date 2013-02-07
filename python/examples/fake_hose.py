import logging, argparse, json, time
import numpy as np
import idport


log = logging.getLogger(__name__)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Stream EEG to IDport')
  parser.add_argument('--hardware_id', default='unknown',
    help='Identifier of the hardware setup.')
  parser.add_argument('--chunk-size', default=16, type=int,
    help='Number of samples to read and send at once.')
  parser.add_argument('--idport-url', default='http://localhost:5000',
    help='URL of IDport REST API')
  parser.add_argument('--user-id', default='test-user')
  parser.add_argument('--stream-id', default='test-stream')
  parser.add_argument('--verbose', '-v', action='store_true')

  args = parser.parse_args()
  
  # Setup output.
  logging.basicConfig(level=logging.INFO)
  if args.verbose:
    log.setLevel(logging.DEBUG)
  np.set_printoptions(precision=2)

  # Setup stream.  
  labels = ['%.2f Hz' % freq for freq in range(4)]

  stream_id = idport.post_stream(args.idport_url, args.user_id, labels, 128, 
    args.hardware_id)
  print stream_id
