-- Please note that I have only a few hours of experience with Lua. So,
-- my code is probably sub-optimal and not idiomatic Lua. Sorry.
idport = require 'idport'

-- Add some helper functions that Lua seems to be missing. --
function isnan(n) return tostring(n) == tostring(0/0) end
function sleep(secs)
  t = os.clock() + secs
  while(os.clock() < t) do
    -- busy loop :/
  end
end

-- Define some MindPlay related functions.
local RESPONSE_READY = 2
local RESPONSE_INVALID = 3

local function cleanup_transfers(list)
  for i, r in ipairs(list) do
    s = idport.response_status(r)
    if (s == RESPONSE_READY) or (s == RESPONSE_INVALID) then
      idport.response_destroy(r)
      table.remove(list, i)
    end
  end
end

-- Initialize API and setup bookkeeping.
local mp = idport.init('localhost:5000')

local user_id ='test_user'
local stream_id = 'test_stream'
local detections = {}
local annotations = {}

-- Start main event loop.
local FPS = 30
local frame = 0
while true do
  frame = frame + 1
  io.write('.'); io.flush()  -- Show progress.

  -- Regularly request a new prediction from the server. --
  if (frame % math.floor(FPS/8)) == 0 then
    -- Perform (non-blocking) request for a detection:
    r = idport.request_detection(mp, user_id, stream_id)
    if r then table.insert(detections, r) end
  end

  if frame % 100 == 0 then
    -- Send annotation.
    r = idport.annotate(mp, user_id, stream_id, 'lua_example', 'Hi!')
    if r then table.insert(annotations, r) end
  end

  -- Update asynchronous transfers in progress:
  idport.update(mp)

  -- Loop over and handle responses:
  for i, r in ipairs(detections) do
    if idport.response_status(r) == RESPONSE_READY then
      print('p = ' .. string.format('%.2f', idport.detection(r, 'random')))
    end
  end

  cleanup_transfers(detections); 
  cleanup_transfers(annotations)

  sleep(1/FPS)
end

-- Cleanup API.
idport.destroy(mp)
