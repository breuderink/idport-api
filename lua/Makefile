# Simple makefile that uses files from the C API in a sibling directory.
# It assumes that the C API has already been built successfully.
LDFLAGS += -lcurl -ljansson -L../c/ -lidport -llua 
 
lua_runner: idport_lua.o
idport_lua.o: CFLAGS += -I../c/
