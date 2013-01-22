#include "idport.h"
#define FPS 30

int main(void)
{
  idp_api_t mp;
  idp_response_t *response = NULL;
  const char *user_id = "test_user", *stream_id = "1";
  float probability;
  int err;

  /* To start using IDport, we setup an API with with a brain-computer
   * interface server address. */
  idp_init(&mp, "http://localhost:5000");


  /* Start the game loop. */
  for(int frame=0;; ++frame) {
    /* Four times a second, we request the server to detect important
     * patterns in the incoming EEG data. To keep this example simple,
     * we don't keep a list with with parallel transfers --- which we
     * recommended for a real game in order to reliably support frequent
     * (> 8 Hz) update rates. */
    if (frame % (FPS / 4) == 0) {
      response = idp_get_detection(&mp, user_id, stream_id);
    }

    /* We hate interrupting your the game. So we update our active
     * requests, without stalling the game: */
    idp_update(&mp);

    /* If we have received  a completed responses from the server, we
     * can use the detected brain state. Here we use a fake detector
     * that gives random result for testing purposes. */
    switch (response->status) {
    case IDP_RESP_READY:
      err = idp_read_detection(response, "random", &probability);
      idp_response_destroy(response); /* Free slot for new requests. */
      if (err) {
        fprintf(stderr, "Could not decode message, code = %d!\n", err);
        exit(-1);
      }

      if (probability > 0.80) {
        printf("Detected random event with high confidence: p = %.2f.\n",
               probability);
      }
      break;

    case IDP_RESP_INVALID:
      fprintf(stderr, "Cleaning up invalid response.\n");
      idp_response_destroy(response); /* Free slot for new requests. */
      break;

    default:
      break;
    }

    printf("."); fflush(stdout); /* Show smooth progress. */
    usleep(1e6/FPS);
  }

  idp_destroy(&mp);
  return 0;
}
