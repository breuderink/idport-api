CFLAGS = -pedantic -std=c99
LDFLAGS = -lcurl -ljansson

all: libmindplay.a(mindplay.o) example_game_loop 
example_game_loop : LDFLAGS += -L. -lmindplay
