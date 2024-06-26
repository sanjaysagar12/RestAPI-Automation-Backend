# RestAPI-Automation-Backend Documentation

RestAPI-Automation-Backend is a Flask-based RESTful API designed to handle user registration, authentication, session management, and API call forwarding.

## Endpoints

### 1. `/register`

- **Method:** POST
- **Description:** Allows users to register by providing email, username, and password. An OTP (One Time Password) is sent to the registered email for verification.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password"
  }
  ```
- **Response**

  ```json
  {
    "valid": true,
    "message": "User registered successfully, please verify OTP sent to email."
  }
  ```

### 2. `/verify`

- **Method:** POST
- **Description:** Verifies the user by confirming the OTP received via email during registration.
- **Request Body:**

  ```json
  {
    "email": "user@example.com",
    "otp": 123456
  }
  ```

- **Response:**

  ```json
  {
    "valid": true,
    "message": "User verified successfully."
  }
  ```

### 3. `/login`

- **Method:** POST
- **Description:** Allows users to login with their email and password. Generates a session token upon successful login.
- **Request Body:**

  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```

### 4. `/profile`

- **Method:** POST
- **Description:** Retrieves the user profile data. Requires a valid token in the request header for authentication.

- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Response:**

  ```json
  {
    "message": "Token is valid.",
    "userdata": { "user_data": "..." },
    "client_ip": "192.168.1.1"
  }
  ```

## Manual Testing

### 5. `/fetch-one`

- **Method:** POST
- **Description:** Forwards an API call with specified method, URL, headers, and body. Requires a valid token in the request header for authentication.
- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Request Body:**

  ```json
  {
    "method": "GET",
    "url": "https://api.example.com/resource",
    "headers": {
      "Authorization": "Bearer token"
    },
    "body": {}
  }
  ```

- **Response:** Returns the response from the forwarded API call.

### 6. `/fetch-many`

- **Method:** POST- **Headers:**

- **Description:** This endpoint accepts a JSON payload containing multiple API call data and returns the responses in a JSON array.

- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Request Body**

  The request body should be a JSON array containing objects with the following fields:

  url (string): The URL of the API to call.
  headers (object): The headers to include in the API call.
  body (object): The body of the API call (if applicable).
  method (string): The HTTP method to use (GET, POST, PUT, DELETE).

- **Request:**

  ```json
  [
    {
      "url": "https://jsonplaceholder.typicode.com/posts/1",
      "headers": {},
      "body": {},
      "method": "GET"
    },
    {
      "url": "https://jsonplaceholder.typicode.com/posts",
      "headers": { "Content-Type": "application/json" },
      "body": { "title": "foo", "body": "bar", "userId": 1 },
      "method": "POST"
    },
    {
      "url": "https://jsonplaceholder.typicode.com/posts/1",
      "headers": { "Content-Type": "application/json" },
      "body": { "title": "foo_updated", "body": "bar_updated", "userId": 1 },
      "method": "PUT"
    },
    {
      "url": "https://jsonplaceholder.typicode.com/posts/1",
      "headers": {},
      "body": {},
      "method": "DELETE"
    }
  ]
  ```

- **Example:**

  ```bash
  curl -X POST http://127.0.0.1:5000/fetch-one \
      -H "Content-Type: application/json" \
      -H "Token: your_token_here" \
      -d '[
            {
              "url": "https://jsonplaceholder.typicode.com/posts/1",
              "headers": {},
              "body": {},
              "method": "GET"
            },
            {
              "url": "https://jsonplaceholder.typicode.com/posts",
              "headers": {"Content-Type": "application/json"},
              "body": {"title": "foo", "body": "bar", "userId": 1},
              "method": "POST"
            },
            {
              "url": "https://jsonplaceholder.typicode.com/posts/1",
              "headers": {"Content-Type": "application/json"},
              "body": {"title": "foo_updated", "body": "bar_updated", "userId": 1},
              "method": "PUT"
            },
            {
              "url": "https://jsonplaceholder.typicode.com/posts/1",
              "headers": {},
              "body": {},
              "method": "DELETE"
            }
          ]'
  ```

- **Responce Body:**

  ```json
  [
    {
      "userId": 1,
      "id": 1,
      "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
      "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
    },
    {
      "title": "foo",
      "body": "bar",
      "userId": 1,
      "id": 101
    },
    {
      "title": "foo_updated",
      "body": "bar_updated",
      "userId": 1,
      "id": 1
    },
    {}
  ]
  ```

### 7. `/save-response`

- **Method:** POST

- **Description:** Saves the request and response data of an API call.

- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Request Body:**
  ```json
   {
    "request": { ... },
    "response": { ... }
  }
  ```

### 8.`/history`

- **Method:** POST
- **Description:**
  Retrieves the history of saved API request and response data.

- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Response:**
  ```json
  {
    "valid": true,
    "data": [ ... ]
  }
  ```

### 9. `/workflow`

- **Method:** POST
- **Description:**
  The Async Workflow Execution Tool is designed to automate a sequence of HTTP API calls with support for dynamic data replacements.
- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Request Body:**
  ```json
  {
    "workflow_data":[...],
    "automation_data":{....}
  }
  ```
- **Example:**

  ```json
  {
    "workflow_data": [
      {
        "tag": "login",
        "method": "POST",
        "url": "http://localhost:8000/login",
        "headers": {},
        "body": {
          "email": "sanjaysagarlearn@gmail.com",
          "password": "12345"
        },
        "cookies": {}
      },
      {
        "tag": "profile",
        "method": "POST",
        "url": "http://localhost:8000/profile",
        "headers": {
          "token": "1qwsdfe32were34ew"
        },
        "body": {},
        "cookies": {}
      },
      {
        "tag": "history",
        "method": "POST",
        "url": "http://localhost:8000/history",
        "headers": {
          "token": "iqdo3do2o3n90231kl"
        },
        "body": {},
        "cookies": {}
      }
    ],
    "automation_data": {
      "login": {
        "1qwsdfe32were34ew": ["(token)", "profile"],
        "iqdo3do2o3n90231kl": ["(token)", "history"]
      }
    }
  }
  ```

## Automation Testing

### 10. `/check-request-code`

- **Method:** POST
- **Description:**
  The /check-request-code endpoint allows users to make a specified HTTP request and check whether the response code matches the expected response code. This is useful for automated testing and validation of API responses.

- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Request Body:**

  ```json
  {
    "method": "string",
    "url": "string",
    "headers": {
      "key": "value"
    },
    "body": {
      "key": "value"
    },
    "expected_code": 200
  }
  ```

- **Response**

  ```json
  {
    "valid": true,
    "message": "Success: The response code matches the expected code.",
    "status_code": 200
  }
  ```

- **Example**

  ```bash
  curl -X POST http://localhost:8000/check-request-code \
  -H "Content-Type: application/json" \
  -H "Token: your-auth-token" \
  -d '{
    "method": "GET",
    "url": "https://api.example.com/endpoint",
    "headers": {
      "Authorization": "Bearer your-token"
    },
    "body": {},
    "expected_code": 200
  }'
  ```

### 11. `/validate-response-schema`

- **Method:** POST
- **Description:**
  The `/validate-response-schema` endpoint allows users to make a specified HTTP request, validate the response body structure against a given schema. This is useful for automated testing and validation of API
- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Request body**

  ```json
  {
    "method": "string",
    "url": "string",
    "headers": {
      "key": "value"
    },
    "body": {
      "key": "value"
    },
    "expected_body_schema": {
      "type": "object",
      "properties": {
        "key": { "type": "type" }
      },
      "required": ["key"]
    }
  }
  ```

- **Response body**

  ```json
  {
    "valid": true,
    "passed": true,
    "message": "Success: The response body matches the expected schema.",

    "status_code": 200,
    "response_body": {
      "id": 1,
      "name": "Example",
      "email": "example@example.com"
    }
  }
  ```

### 12. `/validate-response-body`

- **Method:** POST
- **Description:**
  The `/validate-response-body` endpoint allows users to make a specified HTTP request, validate the response body against a given expected body. This is useful for automated testing and validation of API
- **Request Headers**

  Content-Type: application/json

  Token: <your-auth-token> (Required for session verification)

- **Request body**

  ```json
  {
    "method": "string",
    "url": "string",
    "headers": {
      "key": "value"
    },
    "body": {
      "key": "value"
    },
    "expected_body": {
      "type": "object",
      "properties": {
        "key": { "type": "type" }
      },
      "required": ["key"]
    }
  }
  ```

- **Response body**

  ```json
  {
    "valid": true,
    "passed": true,
    "message": "Success: The response body matches the expected body.",

    "status_code": 200,
    "response_body": {
      "id": 1,
      "name": "Example",
      "email": "example@example.com"
    }
  }
  ```
