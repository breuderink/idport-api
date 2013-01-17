#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#include "mindplay.h"


static int mindplay__init(lua_State *L)
{
  const char *api_url = luaL_checkstring(L, 1);
  const char *user_id= luaL_checkstring(L, 2);
  const char *stream_id = luaL_checkstring(L, 3);

  mp_api_t *mp = lua_newuserdata(L, sizeof(mp_api_t));
  luaL_getmetatable(L, "mindplay.api");
  lua_setmetatable(L, -2);  /* -2 points to the new userdata. */

  mp_init(mp, api_url, user_id, stream_id);

  return 1;
}

static int mindplay__request_detection(lua_State *L)
{
  mp_api_t *mp = luaL_checkudata(L, 1, "mindplay.api");
  mp_response_t **r;
  mp_response_t *response;

  /* We are going to do something dangerous; we push a pointer as
   * userdata into Lua. For this to work, the pointer has to remain
   * valid. Actually, it is not unlike regular C. */

  response = mp_get_detection(mp);
  lua_pushlightuserdata(L, response);

  return 1;  /* return new request struct address. */
}

static int mindplay__update(lua_State *L)
{
  mp_api_t *mp = luaL_checkudata(L, 1, "mindplay.api");
  mp_update(mp);
  return 0;
}

static int mindplay__detection(lua_State *L)
{
  const char *label;
  int err;
  float p;
  mp_response_t *response = NULL;

  /* Is there no luaL_ alternative for light userdata? */
  if (!lua_isuserdata(L, 1)) {
    luaL_error(L, "Argument 1 is not a request!");
  }
  response = lua_touserdata(L, 1);
  label = luaL_checkstring(L, 2);

  err = mp_read_detection(response, label, &p);
  /* We could handle errors here. */
  lua_pushnumber(L, p);

  return 1;  /* return new float. */
}

static int mindplay__response_destroy(lua_State *L)
{
  mp_response_t *response = NULL;

  if (!lua_isuserdata(L, 2)) {
    luaL_error(L, "Argument 2 is not a request!");
  }
  response = lua_touserdata(L, 2);

  mp_response_destroy(response);
  return 0;
}

static int mindplay__destroy(lua_State *L)
{
  mp_api_t *mp = luaL_checkudata(L, 1, "mindplay.api");
  mp_destroy(mp);

  return 0;
}


static const luaL_reg mindplay[] = {
  { "init", mindplay__init },
  { "update", mindplay__update },
  { "request_detection", mindplay__request_detection },
  { "response_destroy", mindplay__response_destroy },
  { "destroy", mindplay__destroy },
  { "detection", mindplay__detection },
  { NULL, NULL }
};


LUALIB_API int luaopen_mindplay(lua_State *L)
{
  luaL_newmetatable(L, "mindplay.api");
  luaL_register(L, "mindplay", mindplay);
  return 1;
}

