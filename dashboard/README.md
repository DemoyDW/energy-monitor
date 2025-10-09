# Dashboard

## Description of the folder 

This folder sets up all of the visualisation and sign up functionality of the dashboard.

## Usage

Provides insights into the energy data.

## Environment set up

### Database connection .env

```
DB_NAME={your db name}
DB_USERNAME={your db username}
DB_PASSWORD={your db password}
DB_PORT={your db port}
DB_HOST={your db host}
```

## How to run the dashboard

### Run locally 

1. Add the environment setup details to your local postgres database in a .env file.
2. run ```streamlit run dashboard.py``` in the terminal.

### Run on the cloud

1. Run the dashboard from the ecs tasks public ip address using port 8501 e.g ```{public ip address}:8501```.

