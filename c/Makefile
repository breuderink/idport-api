CFLAGS = -pedantic -std=c99
LDFLAGS = -lcurl -ljansson

all: libmindplay.a(mindplay.o) example_game_loop example_annotate
example_game_loop example_annotate: LDFLAGS += -L. -lmindplay
example_game_loop example_annotate: libmindplay.a
