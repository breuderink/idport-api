import logging, argparse, json, time
import numpy as np
import idport_samples


log = logging.getLogger(__name__)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Stream EEG to IDPort')
  parser.add_argument('--hardware_id', default='unknown',
    help='Identifier of the hardware setup.')
  parser.add_argument('--chunk-size', default=16, type=int,
    help='Number of samples to read and send at once.')

  parser.add_argument('--idport-url', default='localhost:5000',
    help='URL of IDport REST API')
  parser.add_argument('--idport-user', default='pax-user')
  parser.add_argument('--idport-stream', default='pax-stream')

  parser.add_argument('--verbose', '-v', action='store_true',
    help='Number of samples to read and send at once.')
  args = parser.parse_args()
  
  # Setup output.
  logging.basicConfig(level=logging.INFO)
  if args.verbose:
    log.setLevel(logging.DEBUG)
  np.set_printoptions(precision=2)

  # Setup stream.  
  labels = ['%.2f Hz' % freq for freq in range(4)]
  idport_samples.post_stream(args.idport_url, 
  @@ MOVE TO API? Probably yes.
