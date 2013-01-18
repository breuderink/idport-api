#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

/* Copied from Pax Britannica: */
#define REGISTER_LOADER(module_name, loader) \
  int loader(lua_State *L); \
  lua_pushcfunction(L, loader); \
  lua_setfield(L, -2, module_name)

int main (void)
{
  int error;
  lua_State *L = lua_open();

  luaL_openlibs(L);

  /* <MAGIC> */
  lua_getglobal(L, "package");
  lua_getfield(L, -1, "preload");
  REGISTER_LOADER("idport", luaopen_idport);
  lua_pop(L, 2);
  /* </MAGIC> */

  error = luaL_dofile(L, "main.lua"); /* execute main Lua script. */
  if (error) {
    fprintf(stderr, "%s", lua_tostring(L, -1));
    lua_pop(L, 1);  /* pop error message from the stack */
  }

  lua_close(L);

  return 0;
}
