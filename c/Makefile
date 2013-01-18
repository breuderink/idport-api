CFLAGS = -pedantic -std=c99
LDFLAGS = -lcurl -ljansson

all: libidport.a(idport.o) example_game_loop example_annotate
example_game_loop example_annotate: LDFLAGS += -L. -lidport
example_game_loop example_annotate: libidport.a
