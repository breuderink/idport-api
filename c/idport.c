#include "idport.h"

static char curl_error_buf[CURL_ERROR_SIZE];

static idp_response_t* idp_response_init(idp_api_t *idp, CURL *parent);
static size_t _curl_write_callback(char *ptr, size_t size, size_t nmemb,
                                   void *userdata);

/* Initialize the API. */
void idp_init(idp_api_t *idp, const char *api_url)
{
  /* Copy API specification. */
  strlcpy(idp->api_url, api_url, sizeof(idp->api_url));

  /* Setup curl. */
  idp->multi_handle = curl_multi_init();

  /* Empty response list. */
  for (int i = 0; i < IDP_NREQ; ++i) {
    idp->responses[i].status = IDP_RESP_UNUSED;
  }
}


/* Find and initialize an unused request buffer from the pool. */
static idp_response_t* idp_response_init(idp_api_t *idp, CURL *parent)
{
  idp_response_t *r = NULL;
  for (int i = 0; i < IDP_NREQ; ++i) {
    if (idp->responses[i].status == IDP_RESP_UNUSED) {
      /* We found one. Let's initialize. */
      r = &idp->responses[i];
      r->parent = parent;
      r->header_chunks = NULL;
      r->size = 0;
      memset(r->buffer, 0, IDP_BUFSIZE);
      r->status = IDP_RESP_PENDING;
      break;
    }
  }

  return r;
}


/* Internal function for performing a curl request. */
idp_response_t *do_request(idp_api_t *idp, const char *url)
{
  idp_response_t *response;
  CURL *handle = curl_easy_init();
  if (!handle) {
    return NULL;
  }

  response = idp_response_init(idp, handle);
  if (response == NULL) {
    fprintf(stderr, "No free response slots available!\n");
    return NULL;
  }

  /* Fire an asynchronous HTTP request. */
  curl_easy_setopt(handle, CURLOPT_URL, url);
  curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, _curl_write_callback);
  curl_easy_setopt(handle, CURLOPT_WRITEDATA, response);
  curl_easy_setopt(handle, CURLOPT_ERRORBUFFER, curl_error_buf);
  curl_multi_add_handle(idp->multi_handle, handle);

  return response;
}

/* Request a detection for a user and stream ID. */
idp_response_t *idp_get_detection(idp_api_t *idp,
                                const char *user_id, const char *stream_id)
{
  char url[IDP_URLLEN];
  snprintf(url, sizeof(url),
           "%s/u/%s/s/%s/detection", idp->api_url, user_id, stream_id);
  return do_request(idp, url);
}

idp_response_t *idp_post_annotation(idp_api_t *idp,
                                  const char *user_id, const char *stream_id,
                                  const char *annotator, const char *text,
                                  const double offset, const double duration)
{
  char url[IDP_URLLEN], *payload;
  CURL *handle = curl_easy_init();
  idp_response_t *response;

  response = idp_response_init(idp, handle);
  if (response == NULL) {
    fprintf(stderr, "No free response slots available!\n");
    return NULL;
  }

  snprintf(url, sizeof(url),
           "%s/u/%s/s/%s/annotations", idp->api_url, user_id, stream_id);

  /* Fire an asynchronous HTTP request. */
  curl_easy_setopt(handle, CURLOPT_URL, url);

  /* Create payload. */
  {
    struct timeval t;
    gettimeofday(&t, NULL);
    /* Note that this time is not necessarily monotonously increasing.
     * This is a very difficult subjects. */

    json_t *J = json_pack("{s:s, s:s s:f s:f s:f}",
                          "annotator", annotator,
                          "text", text,
                          "local_time", (double) t.tv_sec + 1e-6 * t.tv_usec,
                          "offset", offset,
                          "duration", duration);
    payload = json_dumps(J, JSON_INDENT(2));
    curl_easy_setopt(handle, CURLOPT_COPYPOSTFIELDS, payload);
    free(payload);
    json_decref(J);
  }



  curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, _curl_write_callback);
  curl_easy_setopt(handle, CURLOPT_WRITEDATA, response);
  curl_easy_setopt(handle, CURLOPT_ERRORBUFFER, curl_error_buf);


  /* Create HTTP header. */
  response->header_chunks = curl_slist_append(
                              response->header_chunks, "Content-Type: application/json");
  curl_easy_setopt(handle, CURLOPT_HTTPHEADER, response->header_chunks);

  curl_multi_add_handle(idp->multi_handle, handle);



  return response;
}


/* Update asynchronous transfers. */
void idp_update(idp_api_t *idp)
{
  int msgs_left, active_handles;
  CURLMsg *msg;
  idp_response_t *response;

  /* Do non-blocking update with curl: */
  curl_multi_perform(idp->multi_handle, &active_handles);

  /* Handle completed curl transfers. */
  while ((msg = curl_multi_info_read(idp->multi_handle, &msgs_left))) {
    if (msg->msg == CURLMSG_DONE) {
      /* Find corresponding response: */
      response = NULL;
      for (int i = 0; i < IDP_NREQ; ++i) {
        if (idp->responses[i].status == IDP_RESP_PENDING &&
            idp->responses[i].parent == msg->easy_handle) {
          response = &idp->responses[i];
          break;
        }
      }
      assert(response);

      /* Check for errors. */
      response->status = IDP_RESP_READY;
      if (msg->data.result != 0) {
        fprintf(stderr, "Request failed: \"%s\".\n", curl_error_buf);
        response->status = IDP_RESP_INVALID;
      }

      /* Cleanup curl transfer. */
      curl_multi_remove_handle(idp->multi_handle, msg->easy_handle);
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
  idp_response_t *b = (idp_response_t *) userdata;

  if (b->size + real_size >= IDP_BUFSIZE) {
    fprintf(stderr, "Response is too large for receiving buffer!\n");
    return -1;  /* Also notify libcurl. */
  }

  memcpy(b->buffer + b->size, ptr, real_size);
  b->size += real_size;
  return real_size;
}


/* Helper function do decode a fully received response from a detection
 * request. */
int idp_read_detection(const idp_response_t *response, const char
                      *detector_name, float *p)
{
  json_t *root, *json;
  json_error_t error;
  int status = 0;

  *p = NAN;

  if (response->status != IDP_RESP_READY) {
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


void idp_destroy(idp_api_t *idp)
{
  /* TODO: handle transfers in progress? */
  curl_multi_cleanup(idp->multi_handle);
}


void idp_response_destroy(idp_response_t *response)
{
  response->status = IDP_RESP_UNUSED;
  curl_slist_free_all(response->header_chunks);
}
