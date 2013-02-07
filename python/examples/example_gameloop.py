import time, argparse, sys
import idport

# Right now, everything is working synchronously. It would be quite easy
# to turn this in to async networking using hooks in request: 
# [1] http://docs.python-requests.org/en/latest/user/advanced/#event-hooks

FPS = 30

if __name__ == '__main__':
  # Add a convenient CLI interface.
  parser = argparse.ArgumentParser(description='Game-loop example.')
  parser.add_argument('--url', default='http://localhost:5000',
    help='URL of IDport REST API')
  parser.add_argument('--user_id', default='test-user')
  parser.add_argument('--stream_id', default='test-stream')

  args = parser.parse_args()

  frame = 0
  while True:
    try:
      if frame % 8 == 0:
        # We request a new detection. For now, this happens in a
        # blocking fashion.
        d = idport.get_detection(args.url, args.user_id, args.stream_id)
        if d['random'] > .9:
          print ('Detected random event with high probability: p=%.2f .' % 
            d['random']),

      #if frame % 100 == 0:
      #  print 'Sending an annotation...'
      #  print idport.post_annotation(args.url, args.user_id, args.stream_id,
      #    'python-example', 'Hi!')

    except NotImplementedError as e:
      print 'Error:', e
    
    sys.stdout.write('.'); sys.stdout.flush()  # show progress.

    time.sleep(1./FPS)
    frame += 1
    
