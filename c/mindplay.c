#include "mindplay.h"

static char curl_error_buf[CURL_ERROR_SIZE];

static mp_response_t* mp_response_init(mp_api_t *mp, CURL *parent);
static size_t _curl_write_callback(char *ptr, size_t size, size_t nmemb,
                                   void *userdata);

/* Initialize the API. */
void mp_init(mp_api_t *mp, const char *api_url)
{
  /* Copy API specification. */
  strlcpy(mp->api_url, api_url, sizeof(mp->api_url));

  /* Setup curl. */
  mp->multi_handle = curl_multi_init();

  /* Empty response list. */
  for (int i = 0; i < MP_NREQ; ++i) {
    mp->responses[i].status = MP_RESP_UNUSED;
  }
}


/* Find and initialize an unused request buffer from the pool. */
static mp_response_t* mp_response_init(mp_api_t *mp, CURL *parent)
{
  for (int i = 0; i < MP_NREQ; ++i) {
    if (mp->responses[i].status == MP_RESP_UNUSED) {
      mp->responses[i].parent = parent;
      mp->responses[i].size = 0;
      memset(mp->responses[i].buffer, 0, MP_BUFSIZE);

      mp->responses[i].status = MP_RESP_PENDING;
      return &mp->responses[i];
    }
  }
  return NULL;  /* All buffers are in use. */
}


/* Request a detection for a user and stream ID. */
mp_response_t *mp_get_detection(mp_api_t *mp, 
  const char *user_id, const char *stream_id)
{
  char url[MP_URLLEN];
  CURL *handle = curl_easy_init();
  mp_response_t *response;

  response = mp_response_init(mp, handle);
  if (response == NULL) {
    fprintf(stderr, "No free response slots available!\n");
    return NULL;
  }

  /* Configure the API URL. */
  snprintf(url, sizeof(url), 
    "%s/u/%s/s/%s/detection", mp->api_url, user_id, stream_id);

  /* Fire an asynchronous HTTP request. */
  curl_easy_setopt(handle, CURLOPT_URL, url);
  curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, _curl_write_callback);
  curl_easy_setopt(handle, CURLOPT_WRITEDATA, response);
  curl_easy_setopt(handle, CURLOPT_ERRORBUFFER, curl_error_buf);
  curl_multi_add_handle(mp->multi_handle, handle);

  return response;
}

/* Update asynchronous transfers. */
void mp_update(mp_api_t *mp)
{
  int msgs_left, active_handles;
  CURLMsg *msg;
  mp_response_t *response;

  /* Do non-blocking update with curl: */
  curl_multi_perform(mp->multi_handle, &active_handles);

  /* Handle completed curl transfers. */
  while ((msg = curl_multi_info_read(mp->multi_handle, &msgs_left))) {
    if (msg->msg == CURLMSG_DONE) {
      /* Find corresponding response: */
      response = NULL;
      for (int i = 0; i < MP_NREQ; ++i) {
        if (mp->responses[i].status == MP_RESP_PENDING && 
            mp->responses[i].parent == msg->easy_handle) {
          response = &mp->responses[i];
          break;
        }
      }
      assert(response);

      /* Check for errors. */
      response->status = MP_RESP_READY;
      if (msg->data.result != 0) {
        fprintf(stderr, "Request failed: \"%s\".\n", curl_error_buf);
        response->status = MP_RESP_INVALID;
      }

      /* Cleanup curl transfer. */
      curl_multi_remove_handle(mp->multi_handle, msg->easy_handle);
      curl_easy_cleanup(msg->easy_handle);
    }
  }
}

/* Write callback to handle incoming data. To be called from within curl. */
static size_t _curl_write_callback(char *ptr, size_t size, size_t nmemb,
                                   void *userdata)
{
  /* We could use dynamic memory allocation, but let's not make it too
   * difficult... */
  size_t real_size = size * nmemb;
  mp_response_t *b = (mp_response_t *) userdata;

  if (b->size + real_size >= MP_BUFSIZE) {
    fprintf(stderr, "Response is too large for receiving buffer!\n");
    return -1;  /* Also notify libcurl. */
  }

  memcpy(b->buffer + b->size, ptr, real_size);
  b->size += real_size;
  return real_size;
}


/* Helper function do decode a fully received response from a detection
 * request. */
int mp_read_detection(const mp_response_t *response, const char
                      *detector_name, float *p)
{
  json_t *root, *json;
  json_error_t error;
  int status = 0;

  *p = NAN;

  if (response->status != MP_RESP_READY) {
    return -1;
  }

  root = json = json_loads(response->buffer, 0, &error);
  if(!json) {
    fprintf(stderr, "JSON Error: on line %d: %s!\n", error.line, error.text);
    status = -2;
    goto cleanup;
  }

  json = json_object_get(json, "detection");
  if (!json) {
    fprintf(stderr, "No detection key in JSON response!\n");
    status = -3;
    goto cleanup;
  }

  json = json_object_get(json, detector_name);
  if (!json) {
    fprintf(stderr,
            "Detector %s not found in JSON response!\n", detector_name);
    status = -4;
    goto cleanup;
  }

  *p = json_real_value(json);

cleanup:
  json_decref(root);
  return status;
}


void mp_destroy(mp_api_t *mp)
{
  /* TODO: handle transfers in progress? */
  curl_multi_cleanup(mp->multi_handle);
}


void mp_response_destroy(mp_response_t *response)
{
  response->status = MP_RESP_UNUSED;
}
