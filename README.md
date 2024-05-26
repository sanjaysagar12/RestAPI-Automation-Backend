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
- **Headers**
  token: Session token
- **Response:**

```json
{
  "message": "Token is valid.",
  "userdata": { "user_data": "..." },
  "client_ip": "192.168.1.1"
}
```

### 5. `/fetch-one`

- **Method:** POST
- **Description:** Forwards an API call with specified method, URL, headers, and body. Requires a valid token in the request header for authentication.
- **Headers**
  token: Session token
- **Request Body:**

```json
Copy code
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

### 6. `/save-response`

- **Method:** POST

- **Description:** Saves the request and response data of an API call.

- **Headers:**
  token: Session token
- **Request Body:**
  ```json
   {
    "request": { ... },
    "response": { ... }
  }
  ```

### 7.`/history`

- **Method:** POST
- **Description:** Retrieves the history of saved API request and response data.

- **Headers**
  token: Session token
- **Request Body:**
  ```json
  {
    "valid": true,
    "data": [ ... ]
  }
  ```
