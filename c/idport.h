#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <unistd.h>
#include <math.h>

#include <curl/curl.h>
#include <jansson.h>      /* Can be installed easily with Homebrew on OSX. */

#define IDP_URLLEN 256
#define IDP_NREQ 32        /* Maximum simultaneous requests. */
#define IDP_BUFSIZE 4048   /* Maximum size of response. */


/* Define structure to hold partial or complete server response. */
typedef struct {
  char buffer[IDP_BUFSIZE];
  size_t size;
  enum {IDP_RESP_UNUSED, IDP_RESP_PENDING, IDP_RESP_READY, IDP_RESP_INVALID} 
    status;
  CURL *parent; /* Used to link response and handle after transfer. */
  struct curl_slist *header_chunks; /* Used for HTTP request header. */
} idp_response_t;


/* Structure to hold server state. */
typedef struct {
  char api_url[IDP_URLLEN];
  idp_response_t responses[IDP_NREQ];
  CURLM *multi_handle;
} idp_api_t;


/* Initialize API. */
void idp_init(idp_api_t *mp, const char *api_url);

/* Create a new data stream. */
/* idp_response_t *idp_post_stream(idp_api_t *mp, 
  const char *user_id, const char *stream_id);
*/

/* Add samples or annotations to a stream. */
idp_response_t *idp_post_samples(idp_api_t *mp, 
  const char *user_id, const char *stream_id);
idp_response_t *idp_post_annotation(idp_api_t *mp, 
  const char *user_id, const char *stream_id, 
  const char *annotator, const char *message);

/* Perform asynchronous communication. */
void idp_update(idp_api_t *mp);

/* Request a detection. */
idp_response_t *idp_get_detection(idp_api_t *mp,
  const char *user_id, const char *stream_id);
int idp_read_detection(const idp_response_t *response, const char
                      *detector_name, float *probability); void

/* Clean up a handled request. */
idp_response_destroy(idp_response_t *response);

/* Finally, close the API. */
void idp_destroy(idp_api_t *mp);
