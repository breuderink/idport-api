import time, random
import flask
from flask import request, g


app = flask.Flask(__name__)


@app.before_request
def before_request():
  # We could setup a link to the database here.
  pass


@app.route('/u/<user_id>/s/<stream_id>/detection')
def get_detection(user_id, stream_id):
  time.sleep(.1)  # Simulate processing time.
  scores = {'random' : random.random()}
  return flask.jsonify(detection=scores, user_id=user_id, stream_id=stream_id)


@app.route('/u/<user_id>/s/<stream_id>/annotations', methods=['POST'])
def post_annotation(user_id, stream_id):
  if request.headers['Content-Type'] == 'application/json':
    d = flask.json.loads(request.data)
    app.logger.debug(d)
    return flask.jsonify(status='OK')
  flask.abort(406)  # not acceptable


if __name__ == '__main__':
  app.run(debug=True)
