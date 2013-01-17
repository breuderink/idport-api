-- TODO: add error handling. 404 fill the queue and lead to segmentation
-- error.
mindplay = require 'mindplay'

-- Add test for NaN's. Just using n~=n does not seem to cut it.
function isnan(n) return tostring(n) == tostring(0/0) end

-- Lua doesn't have a native sleep :/.
function sleep(secs)
  t = os.clock() + secs
  while(os.clock() < t) do
    -- busy loop :/
  end
end

FPS = 30
user_id ='test_user'
stream_id = '1'

-- Initialize API:
mp = mindplay.init('localhost:5000')
responses = {}

for i=0,10000 do
  print('Frame ' .. i .. '.');
  print('In transerfer: ' .. #responses ..'.')

  -- Update transfers in progress:
  if (i % math.floor(FPS/8)) == 0 then
    -- Perform (non-blocking) request for a detection:
    print('Requesting prediction...')
    table.insert(responses, mindplay.request_detection(mp, user_id, stream_id))
  end
  mindplay.update(mp)

  -- Try to read the probability from the response. If it is not yet
  -- ready, we get a NaN.
  for i, mp_response in ipairs(responses) do
    p = mindplay.detection(mp_response, 'random')
    if not isnan(p) then 
      print('Detected random event: '.. p) 
      mindplay.response_destroy(mp_response)
      table.remove(responses, i)
    end
  end

  sleep(1/FPS)
end

mindplay.destroy(mp)
