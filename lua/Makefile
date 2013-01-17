# Simple makefile that uses files from the C API in a sibling directory.
# It assumes that the C API has already been built successfully.
LDFLAGS += -lcurl -ljansson -L../c/ -lmindplay -llua 
 
lua_runner: mindplay_lua.o
mindplay_lua.o: CFLAGS += -I../c/
