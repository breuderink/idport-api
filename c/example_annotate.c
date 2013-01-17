#include "mindplay.h"

int main(void)
{
  mp_api_t mp;
  mp_response_t *response = NULL;
  const char *user_id = "test_user", *stream_id = "1";
  int err;

  /* To start using MindPlay, we setup an API with with a server
   * address. */
  mp_init(&mp, "http://localhost:5000");

  printf("Sending an annotation...\n");
  response = mp_post_annotation(&mp, user_id, stream_id, 
      "game_loop_example", "tick");
  printf("Done.\n");
  while (1) {

    /* We hate interrupting the game. So we poll for a response: */
    mp_update(&mp);

    switch (response->status) {
      case MP_RESP_READY:
        printf("And it is ready...");
        /* There is a complete response from the server. Lets extract a
         * probability from the "random" detector: */
        mp_response_destroy(response); /* Free slot for new requests. */
        exit(0);

      case MP_RESP_INVALID:
        printf("And it is invalid...");
        fprintf(stderr, "Cleaning up invalid response.\n");
        mp_response_destroy(response); /* Free slot for new requests. */
        break;

      default:
        break;
    }

    printf("."); fflush(stdout);
    usleep(1e6/10);
  }

  mp_destroy(&mp);
  return 0;
}
