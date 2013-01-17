import time, random
#import numpy as np
import flask
from flask import request, g


app = flask.Flask(__name__)

#def float32_to_string(a):
#  a = np.asarray(a)
#  return a.astype('<f4').tostring().encode('base64)')
#
#
#def string_to_float32(s):
#  return np.fromstring(s.decode('base64'), '<f4')


@app.before_request
def before_request():
  # We could setup a link to the database here.
  pass


@app.route('/u/<user_id>/s/<stream_id>/detection')
def get_detection(user_id, stream_id):
  time.sleep(.1)  # Simulate processing time.
  scores = {'random' : random.random()}
  return flask.jsonify(detection=scores)


if __name__ == '__main__':
  app.run(debug=True)

#@app.route('/u/<user_id>/s', methods=['POST'])
#def create_stream(user_id):
#  # Parse requested stream configuration:
#  h = flask.json.loads(request.data)
#  lab = map(unicode, list(h['sensor_labels']))
#  fs = float(h['sample_rate'])
#
#  # TODO handle exception for excessive streams.
#  stream_id = g.db.create_stream(user_id, lab, fs)
#  return flask.jsonify(user_id=user_id, stream_id=stream_id)
#
#
#@app.route('/u/<user_id>/s/<stream_id>/samples', methods=['POST'])
#def samples(user_id, stream_id):
#  # Parse requested header:
#  d = flask.json.loads(request.data)
#  try:
#    t = float(d['local_start_time'])
#    s = [string_to_float32(s) for s in d['samples']]
#  except:
#    flask.abort(400)  # bad request
#  samples = Samples(local_start_time=t, samples=s)
#  n = g.db.add_samples(user_id, stream_id, samples)
#
#  return flask.jsonify(status='OK', nsamples=n)
#
#
#@app.route('/u/<user_id>/s/<stream_id>/annotations', methods=['POST'])
#def annotation(user_id, stream_id):
#  d = flask.json.loads(request.data)
#
#  try:
#    text = unicode(d['text'])
#    lstart = float(d['local_start_time'])
#    annotator = unicode(d.get('annotator', 'unspecified'))
#    duration = float(d.get('duration', 0.))
#    sstart = None
#    if 'start_sample_number' in d:
#      sstart = int(d['start_sample_number'])
#  except:
#    flask.abort(400)  # bad request
#
#  a = Annotation(text, annotator, lstart, duration, sstart)
#  n = g.db.add_annotation(user_id, stream_id, a)
#
#  return flask.jsonify(status='OK', annotations=n)
#
#


