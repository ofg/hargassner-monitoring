# Feature Descriptions

## Token Caching to Mitigate Rate Limiting

Since beginning of 2026, Hargassner has introduced rate limiting of the login POST request.
Pulling data every 1 or 3 minutes with a new log-in will exceed the rate limit after some time
and thus fails with HTTP status code 429.

To mitigate this, a flag in `config.yml` has been introduced. If `cache_token` is set to `true`,
the program will save the retrieved access credentials into a JSON file. If the JSON file is
present, it will read the token from the JSON file and only request a new token if the token has
expired. The new token will be saved again to the file. The file will be stored in the execution
directory of the program. The file is named `token-cache.json`.

The JSON file has the following structure:

```json
{
    "access_token": "<token string>",
    "refresh_token": "<token string>",
    "expires_in": 3600,
    "expires_at": "2026-03-31T14:35:00+00:00"
}
```

- `access_token`: The Bearer token used to authenticate API requests.
- `refresh_token`: Token used to obtain a new access token.
- `expires_in`: Lifetime of the token in seconds, as returned by the server.
- `expires_at`: Absolute expiration time in UTC (ISO 8601 format), calculated at token retrieval time.

When the current UTC time reaches `expires_at` minus 10 minutes, the program considers the token
expired and requests a new one from the server.

Implemented changes in the repository:

- `config_template.yml` contains the new `cache_token` flag in the `hargassner_web` section.
- `hg_web_api.py` stores tokens in `token-cache.json` in the current execution directory.
- On startup, the program reuses the cached access token if it is still valid for more than 10 minutes.
- If the cache file is missing, expired, or invalid, the program logs a warning or debug message and requests a new token.
- After a successful login, the program writes the new token data back to the cache file.
