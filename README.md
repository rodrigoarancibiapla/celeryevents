# Celery Events Project

This project uses Docker Compose to manage the required services. Follow the instructions below to set up and run the environment.

## Prerequisites

Make sure you have the following programs installed on your machine:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Setup

1. Clone this repository to your local machine:
   ```bash
   git clone <REPOSITORY_URL>
   cd celeryevents
   ```

2. Ensure the docker-compose.yml file is properly configured for your environment.

## Running the Project
To start the services defined in docker-compose.yml, run the following command from the project root:
```
docker-compose up
```
This will start all the containers defined in the docker-compose.yml file.

## Additional Options
To run the containers in detached mode (in the background), use:

```
docker-compose up --build
```
To stop the containers, run:

```
docker-compose down
```

## Project Structure
customersAPI/: API for managing customers.

transactionsAPI/: API for managing transactions.

initSpanner/: Initialization scripts for Google Spanner.

worker/: Background processing services.

flow/: Background processing services to consolidate data.


## Notes
Ensure that the ports defined in docker-compose.yml are not being used by other services.
If you need to rebuild the containers, use:
You're all set! You can now work with the project. 