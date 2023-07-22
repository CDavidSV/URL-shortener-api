# URL-shortener-api
 Simple implementation of a URL shortener application

## Getting Started
This API provides a simple and efficient way to shorten long URLs into shorter, more manageable links. It's a valuable tool for applications   that share concise links, save character space and track link usage.

**Make sure to have Python 3.11 or above installed**

1. Clone the repository
2. install the necessary dependencies from the `requirements.txt` file
3. While uvicorn is not strictly necessary it is recommended.
4. run `uvicorn app.main:app --host <IP> --port <port>` to start the server.

## Required Libraries
- [FastAPI](https://fastapi.tiangolo.com/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [python-jose](https://pypi.org/project/python-jose/)
- [pydantic](https://pypi.org/project/pydantic/)
- [starlette](https://www.starlette.io/)

## Authentication

| Endpoint                | Method | Description                                                |
|-------------------------|--------|------------------------------------------------------------|
| `/user/create`          | POST   | Allows users to create a new account.                     |
| `/user/login`           | POST   | Allows users to log in and obtain an access token.        |

### 1. Register New User

**Endpoint**: `POST /user/create`

This endpoint allows users to create a new account by providing their details.

**Request:**

- Method: POST

JSON Payload:

```JSON
{
    "first_name": "User's First Name",
    "last_name": "User's Last Name",
    "email": "user@example.com",
    "username": "desired_username",
    "password": "user_password"
}
```

**Response:**

- Status Code: 200 OK

JSON Response:

```JSON
{
    "detail": "Account creation successful",
    "token": "YOUR_ACCESS_TOKEN",
    "token_type": "bearer"
}
```

### 2. User Login

**Endpoint**: `POST /user/login`

This endpoint allows users to log in and obtain an access token for accessing protected resources.

**Request:**

- Method: POST

Form Data:

`username=your_username&password=your_password`


**Response:**

- Status Code: 200 OK

JSON Response:

```JSON
{
   "token": "YOUR_ACCESS_TOKEN",
   "token-type": "bearer"
}
```

### 3. Error Responses

If there is an issue with the login process, the API will return an error response with the appropriate status code and message.

| Status Code           | Description                         |
|-----------------------|-------------------------------------|
| 401 Unauthorized      | Incorrect username or password.     |
| 409 Conflict          | Email or username already in use.   |

### 4. How to use the Access Token

To access protected resources, you must include the access token in the `Authorization` header of your HTTP request. Set the header as follows:

`Authorization: Bearer YOUR_ACCESS_TOKEN`

Please note that this is a basic authentication system and may require additional security measures.


## Endpoints

Replace `YOUR_ACCESS_TOKEN` with the token received from the login or account creation response.

| Endpoint                                    | Method | Description                                          |
|---------------------------------------------|--------|------------------------------------------------------|
| `/api/v1/urls/create`                       | POST   | Create a shortened URL.                              |
| `/api/v1/urls/delete`                       | DELETE | Delete a previously created shortened URL.          |
| `/api/v1/urls`                              | GET    | Get a list of short URLs created by the current user.|
| `/api/v1/urls/{url_id}/qr`                  | GET    | Get a QR code image for a specific short URL.        |
| `/api/v1/urls/{url_id}/info`                | GET    | Get information about a specific short URL.          |


### 1. Create shortened URL

**Endpoint:** `POST /api/v1/urls/create`

Request:

- Method: POST

JSON Payload:
```JSON
{
  "title": "Optional title for the URL",
  "back_half": "Custom back half or leave empty for random",
  "original_URL": "The original long URL to shorten"
}
```

### 2. Delete shortened URL
**Endpoint:** `DELETE /api/v1/urls/delete`

Request:

- Method: DELETE

Query Parameter:

`url_id=SHORT_URL_ID_TO_DELETE
`

### 3. Get User's Short URLs

**Endpoint:** `GET /api/v1/urls`

*Note: This returns URLs for the currently logged-in user.*

Request:

- Method: GET

JSON Response:
```JSON
{
  "detail": "success",
  "item_count": "Number of short URLs",
  "short_urls": [
    {
      "title": "Title of the short URL",
      "back_half": "Short URL identifier",
      "original_URL": "Original long URL",
      "creation_date": "Date the short URL was created (format: 'YYYY-MM-DD')",
      "times_visited": "Number of times the short URL has been visited"
    }
  ],
  "user": "Current user's username"
}
```

### 4. Get QR for short URL

**Endpoint:** `GET /api/v1/urls/{url_id}/qr`

Request:

- Method: GET

Image Response: (Image is in PNG format)

### 5. Get Short URL Information

**Endpoint:** `GET /api/v1/urls/{url_id}/info`

Request:

- Method: GET

JSON Response:

```JSON
{
  "detail": "success",
  "data": {
    "title": "Title of the short URL",
    "back_half": "Short URL identifier",
    "original_URL": "Original long URL",
    "creation_date": "Date the short URL was created (format: 'YYYY-MM-DD')",
    "times_visited": "Number of times the short URL has been visited"
  },
  "owner": "Username of the short URL creator"
}
```
