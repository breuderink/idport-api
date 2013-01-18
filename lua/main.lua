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
stream_id = 'test_stream'

-- Initialize API:
mp = mindplay.init('localhost:5000')
detections = {}
annotations = {}

--
READY = 2
INVALID = 3
function cleanup_transfers(list)
  for i, r in ipairs(list) do
    s = mindplay.response_status(r)
    if (s == 2) or (s == 3) then
      mindplay.response_destroy(r)
      table.remove(list, i)
    end
  end
end

-- Start main event loop.
for i=0,10000 do
  print('Frame ' .. i .. ', ' .. 
    #detections + #annotations.. ' responses in transfer.')

  -- Regularly request a new prediction from the server:
  if (i % math.floor(FPS/8)) == 0 then
    -- Perform (non-blocking) request for a detection:
    table.insert(detections, mindplay.request_detection(mp, user_id, stream_id))
  end
  if i % 20 == 0 then
    -- Send annotation with the current frame.
    msg = 'frame ' .. i
    table.insert(annotations, mindplay.annotate(mp, 
      user_id, stream_id, 'lua_example', msg))
  end

  -- Update asynchronous transfers in progress:
  mindplay.update(mp)

  -- Loop over and handle responses:
  for i, r in ipairs(detections) do
    if mindplay.response_status(r) == READY then
      p = mindplay.detection(r, 'random')
      print('p = ' .. p)
    end
  end

  cleanup_transfers(detections)
  cleanup_transfers(annotations)

  sleep(1/FPS)
end

mindplay.destroy(mp)
