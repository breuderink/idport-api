#include "idport.h"

int main(void)
{
  idp_api_t mp;
  idp_response_t *response = NULL;
  const char *user_id = "test_user", *stream_id = "1";

  /* To start using MindPlay, we setup an API with with a server
   * address. */
  idp_init(&mp, "http://localhost:5000");

  printf("Sending an annotation...\n");
  response = idp_post_annotation(&mp, user_id, stream_id, 
    "me", "Tick.", -1, 10);

  while (1) {
    /* We hate interrupting the game. So we poll for a response: */
    idp_update(&mp);

    switch (response->status) {
    case IDP_RESP_READY:
      /* There is a complete response from the server. Lets extract a
       * probability from the "random" detector: */
      printf("Done.\n");
      idp_response_destroy(response); /* Free slot for new requests. */
      exit(0);

    case IDP_RESP_INVALID:
      idp_response_destroy(response); /* Free slot for new requests. */
      exit(-1);

    default:
      break;
    }

    usleep(1e6/100);
  }

  idp_destroy(&mp);
  return 0;
}
