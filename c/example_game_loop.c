#include "idport.h"
#define FPS 30

int main(void)
{
  mp_api_t mp;
  mp_response_t *response = NULL;
  const char *user_id = "test_user", *stream_id = "1";
  float probability;
  int err;

  /* To start using MindPlay, we setup an API with with a server
   * address. */
  mp_init(&mp, "http://localhost:5000");


  /* Start the game loop. */
  for(int frame=0;; ++frame) {
    /* Four times a second, we request a detection from the server.
     * For simplicity, we don't have a queue for transfers in
     * progress, but that probably is a good idea. */
    if (frame % (FPS / 4) == 0) {
      response = mp_get_detection(&mp, user_id, stream_id);
    }

    /* We hate interrupting the game. So we poll for a response: */
    mp_update(&mp);

    /* Handle completed responses from the server. */
    switch (response->status) {
    case MP_RESP_READY:
      /* There is a complete response from the server. Lets extract a
       * probability from the "random" detector: */
      err = mp_read_detection(response, "random", &probability);
      mp_response_destroy(response); /* Free slot for new requests. */
      if (err) {
        fprintf(stderr, "Could not decode message, code = %d!\n", err);
        exit(-1);
      }

      if (probability > 0.80) {
        printf("Detected random event with high confidence: p = %.2f.\n",
               probability);
      }
      break;

    case MP_RESP_INVALID:
      printf("And it is invalid...");
      fprintf(stderr, "Cleaning up invalid response.\n");
      mp_response_destroy(response); /* Free slot for new requests. */
      break;

    default:
      break;
    }

    printf(".");
    fflush(stdout);
    usleep(1e6/FPS);
  }

  mp_destroy(&mp);
  return 0;
}
