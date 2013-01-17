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
-- Initialize API:
mp = mindplay.init('localhost:5000', 'test_user', '1')

for i=0,10000 do
  print('Frame ' .. i .. '.');
  -- Update transfers in progress:
  if (i % math.floor(FPS/3)) == 0 then
    -- Perform (non-blocking) request for a detection:
    print('Requesting prediction...')
    response = mindplay.request_detection(mp)
    FIXME: FUCK, git fout.
  end
  mindplay.update(mp)

  -- Try to read the probability from the response. If it is not yet
  -- received, ready, we get a NaN.
  if (response ~= nil) then
    p = mindplay.detection(response, 'blink')
    if not isnan(p) then 
      print('Detected blink: '.. p) 
      mindplay.response_destroy(response)
      response = nil
    end
  end

  sleep(1/FPS)
end

mindplay.destroy(mp)
