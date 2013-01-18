-- Please note that I have only a few hours of experience with Lua. So,
-- my code is probably sub-optimal and not idiomatic Lua. Sorry.
mindplay = require 'mindplay'

-- Add some helper functions that Lua seems to be missing. --
function isnan(n) return tostring(n) == tostring(0/0) end

-- Lua doesn't have a native sleep?
function sleep(secs)
  t = os.clock() + secs
  while(os.clock() < t) do
    -- busy loop :/
  end
end

--
local RESPONSE_READY = 2
local RESPONSE_INVALID = 3
local FPS = 30
local user_id ='test_user'
local stream_id = 'test_stream'


local function cleanup_transfers(list)
  for i, r in ipairs(list) do
    s = mindplay.response_status(r)
    if (s == RESPONSE_READY) or (s == RESPONSE_INVALID) then
      mindplay.response_destroy(r)
      table.remove(list, i)
    end
  end
end

-- Initialize API:
local mp = mindplay.init('localhost:5000')
local detections = {}
local annotations = {}

-- Start main event loop.
for i=0,10000 do
  print('Frame ' .. i .. ', ' .. 
    #detections + #annotations.. ' responses in transfer.')

  -- Regularly request a new prediction from the server:
  if (i % math.floor(FPS/8)) == 0 then
    -- Perform (non-blocking) request for a detection:
    r = mindplay.request_detection(mp, user_id, stream_id)
    if r then
      table.insert(detections, r)
    else
      print('Cannot perform request!')
    end
  end
  if i % 20 == 0 then
    -- Send annotation with the current frame.
    msg = 'frame ' .. i
    r = mindplay.annotate(mp, user_id, stream_id, 'lua_example', msg)
    if r then
      table.insert(annotations, r)
    else
      print('Cannot perform request!')
    end
  end

  -- Update asynchronous transfers in progress:
  mindplay.update(mp)

  -- Loop over and handle responses:
  for i, r in ipairs(detections) do
    print(r)
    if mindplay.response_status(r) == RESPONSE_READY then
      p = mindplay.detection(r, 'random')
      print('p = ' .. p)
    end
  end

  cleanup_transfers(detections)
  cleanup_transfers(annotations)

  sleep(1/FPS)
end

-- Cleanup again.
mindplay.destroy(mp)
