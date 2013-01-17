#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <unistd.h>
#include <math.h>

#include <curl/curl.h>
#include <jansson.h>      /* Can be installed easily with Homebrew on OSX. */

#define MP_URLLEN 256
#define MP_NREQ 32        /* Maximum simultaneous requests. */
#define MP_BUFSIZE 4048   /* Maximum size of response. */


/* Define structure to hold partial or complete server response. */
typedef struct {
  char buffer[MP_BUFSIZE];
  size_t size;
  enum {MP_RESP_UNUSED, MP_RESP_PENDING, MP_RESP_READY, MP_RESP_INVALID} 
    status;
  CURL *parent; /* Used to link response and handle after transfer. */
} mp_response_t;


/* Structure to hold server state. */
typedef struct {
  char api_url[MP_URLLEN];
  mp_response_t responses[MP_NREQ];
  CURLM *multi_handle;
} mp_api_t;


/* Initialize API. */
void mp_init(mp_api_t *mp, const char *api_url);

/* Create a new data stream. */
/* mp_response_t *mp_post_stream(mp_api_t *mp, 
  const char *user_id, const char *stream_id);
*/

/* Add samples or annotations to a stream. */
mp_response_t *mp_post_samples(mp_api_t *mp, 
  const char *user_id, const char *stream_id);
mp_response_t *mp_post_annotation(mp_api_t *mp, 
  const char *user_id, const char *stream_id, 
  const char *annotator, const char *message);

/* Perform asynchronous communication. */
void mp_update(mp_api_t *mp);

/* Request a detection. */
mp_response_t *mp_get_detection(mp_api_t *mp,
  const char *user_id, const char *stream_id);
int mp_read_detection(const mp_response_t *response, const char
                      *detector_name, float *probability); void

/* Clean up a handled request. */
mp_response_destroy(mp_response_t *response);

/* Finally, close the API. */
void mp_destroy(mp_api_t *mp);
