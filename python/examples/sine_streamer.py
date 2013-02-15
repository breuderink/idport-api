import logging, argparse, json, time
import numpy as np
import idport


log = logging.getLogger(__name__)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Stream EEG to IDport')
  parser.add_argument('--hardware-id', default='unknown',
    help='Identifier of the hardware setup.')
  parser.add_argument('--chunk-size', default=16, type=int,
    help='Number of samples to read and send at once.')
  parser.add_argument('--idport-url', default='http://localhost:8080',
    help='URL of IDport REST API.')
  parser.add_argument('--user-id', default='test-user')
  parser.add_argument('--stream-id', default='test-stream')
  parser.add_argument('--sample_rate', type=float, default=128.)
  parser.add_argument('--verbose', '-v', action='store_true')

  args = parser.parse_args()
  
  # Setup output.
  logging.basicConfig(level=logging.WARNING)
  if args.verbose:
    log.setLevel(logging.DEBUG)
  else:
    log.setLevel(logging.INFO)
  np.set_printoptions(precision=2)

  # Setup stream.  
  freqs = np.arange(4)
  labels = ['%.2f Hz sine' % freq for freq in freqs]
  stream_config = idport.StreamConfig(labels, args.sample_rate,
    args.hardware_id)
  stream_id = idport.post_stream(args.idport_url, args.user_id, stream_config)
  log.info('Created stream %s.', stream_id)

  # Start streaming sine waves.
  log.info('Streaming...')
  i = 0
  duration = args.chunk_size / args.sample_rate
  while True:
    next_t = time.time() + duration

    # Create new samples.
    C = i + np.hstack([np.arange(args.chunk_size).reshape(-1, 1)] * len(freqs))
    T = C / args.sample_rate
    S = np.sin(T * freqs)

    # Post samples to server.
    idport.post_samples(args.idport_url, args.user_id, stream_id, 
      idport.Samples(S, time.time()))
    
    # Update sample count and wait appropriate time.
    i += args.chunk_size
    time.sleep(max(0, next_t - time.time()))
