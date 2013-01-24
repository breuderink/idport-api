#!/usr/bin/env python
import requests

s = requests.session()
print s.config
#s.config['keep_alive'] = False

for i in xrange(100):
  print i
  r = s.get('http://dev.cortext.nl')
print r.text
