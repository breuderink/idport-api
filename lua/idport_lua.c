#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>

#include "idport.h"


static int idport__init(lua_State *L)
{
  const char *api_url = luaL_checkstring(L, 1);

  idp_api_t *idp = lua_newuserdata(L, sizeof(idp_api_t));
  luaL_getmetatable(L, "idport.api");
  lua_setmetatable(L, -2);  /* -2 points to the new userdata. */

  idp_init(idp, api_url);

  return 1;
}


static int idport__request_detection(lua_State *L)
{
  idp_api_t *idp = luaL_checkudata(L, 1, "idport.api");
  const char *user_id= luaL_checkstring(L, 2);
  const char *stream_id = luaL_checkstring(L, 3);
  idp_response_t *response;

  /* We are going to do something dangerous; we push a pointer as
   * userdata into Lua. For this to work, the pointer has to remain
   * valid. Actually, it is not unlike regular C. */

  response = idp_get_detection(idp, user_id, stream_id);
  if (response) {
    lua_pushlightuserdata(L, response);
    return 1;
  }
  return 0;
}


static int idport__update(lua_State *L)
{
  idp_api_t *idp = luaL_checkudata(L, 1, "idport.api");
  idp_update(idp);
  return 0;
}


static int idport__detection(lua_State *L)
{
  const char *label;
  int err;
  float p;
  idp_response_t *response = NULL;

  /* Is there no luaL_ alternative for light userdata? */
  if (!lua_isuserdata(L, 1)) {
    luaL_error(L, "Argument 1 is not a request!");
  }
  response = lua_touserdata(L, 1);
  label = luaL_checkstring(L, 2);

  err = idp_read_detection(response, label, &p);
  /* TODO: we could handle errors here. */
  lua_pushnumber(L, p);

  return 1;  /* return new float. */
}


static int idport__annotate(lua_State *L)
{
  /* TODO: use a table instead of positional arguments, and implement
   * handling of the offset and duration attributes. */
  idp_api_t *idp = luaL_checkudata(L, 1, "idport.api");
  const char *user_id = luaL_checkstring(L, 2);
  const char *stream_id = luaL_checkstring(L, 3);
  const char *annotator = luaL_checkstring(L, 4);
  const char *text = luaL_checkstring(L, 5);
  idp_response_t *response;

  response = idp_post_annotation(idp, user_id, stream_id, annotator,
    text, 0, 0);
  if (response) {
    lua_pushlightuserdata(L, response);
    return 1;
  }
  return 0;
}


static int idport__response_status(lua_State *L)
{
  idp_response_t *response = NULL;

  if (!lua_isuserdata(L, 1)) {
    luaL_error(L, "Argument 1 is not a request!");
  }
  response = lua_touserdata(L, 1);
  lua_pushnumber(L, response->status);

  return 1;
}

static int idport__response_destroy(lua_State *L)
{
  idp_response_t *response = NULL;

  if (!lua_isuserdata(L, 1)) {
    luaL_error(L, "Argument 1 is not a request!");
  }
  response = lua_touserdata(L, 1);

  idp_response_destroy(response);
  return 0;
}


static int idport__destroy(lua_State *L)
{
  idp_api_t *idp = luaL_checkudata(L, 1, "idport.api");
  idp_destroy(idp);

  return 0;
}


static const luaL_reg idport[] = {
  { "init", idport__init },
  { "update", idport__update },
  { "request_detection", idport__request_detection },
  { "annotate", idport__annotate },
  { "response_status", idport__response_status },
  { "response_destroy", idport__response_destroy },
  { "destroy", idport__destroy },
  { "detection", idport__detection },
  { NULL, NULL }
};


LUALIB_API int luaopen_idport(lua_State *L)
{
  luaL_newmetatable(L, "idport.api");
  luaL_register(L, "idport", idport);
  return 1;
}
