# RestAPI-Automation-Backend

## Requirements

- Python 3.7+
- Docker

## Installation

1. **Clone the repository**

   `git clone git@github.com:sanjaysagar12/MailAPI.git`

   Change directory to MailAPI

   `cd RestAPI-Automation-Backend`

2. **Install the required packages**

   `pip install -r requirements.txt`

3. **Run setup.py**

   `python3 setup.py`

4. **Run docker-compose**

   `docker-compose up -d`

5. **Start the FastAPI server**
   `uvicorn main:app --reload`

## The application will be available at http://localhost:8000

**Accessing the API Documentation**
When you run your FastAPI application, you can access the documentation in two formats:

#### Swagger UI:

- Accessible at http://127.0.0.1:8000/docs by default.
- Provides an interactive interface where you can see all the endpoints, their request methods, - parameters, and responses.
- Allows you to make requests to the API endpoints directly from the browser.

#### ReDoc:

- Accessible at http://127.0.0.1:8000/redoc by default.
- Provides a more detailed and structured view of the API documentation.
- Focuses on readability and is useful for understanding the overall API structure.

**Accessing the Mongo Express**

After starting docker-compose, open your web browser and navigate to http://localhost:9090 (or whatever port you specified in your configuration file). You should see the Mongo Express interface where you can interact with your MongoDB databases.

# RestAPI-Automation-Backend
