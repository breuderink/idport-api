#include "mindplay.h"
#define FPS 30

int main(void)
{
  mp_api_t mp;
  mp_response_t *response = NULL;
  float probability;
  int err;

  /* To start using MindPlay, we setup an API with with a server address, a
   * user and a stream to analyze: */
  mp_init(&mp, "http://localhost:5000", "test_user", "1");


  for(int frame=0;; ++frame) {
    if (frame % (FPS / 4) == 0) {
      /* Four times a second, we request a detection from the server: */
      response = mp_get_detection(&mp);
    }

    /* We hate interrupting the game. So we poll for a response: */
    mp_update(&mp);

    /* TODO: loop over response list. In API? */
    if (response->status == MP_RESP_READY) {
      /* There is a complete response from the server. Lets extract a
       * probability from the "left hand" detector: */
      err = mp_read_detection(response, "left hand", &probability);
      mp_response_destroy(response); /* Free slot for new requests. */
      if (err) {
        fprintf(stderr, "Could not decode message, code = %d!\n", err);
        exit(-1);
      }

      if (probability > 0.80) {
        printf("Detected imagined movement with high confidence: p = %.2f.\n",
               probability);
      }
    }

    printf("[Insert your game code for frame %d.]\n", frame);
    usleep(1e6/FPS);
  }

  mp_destroy(&mp);
  return 0;
}
