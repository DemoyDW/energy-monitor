# Description

This folder sets up all of the visualisations and sign up functionality of the dashboard. These scripts read from the centralised RDS database and create charts, graphs and map visualisations on power generation, carbon insights, power outages and energy prices across UK regions. These visualisations are then organised and uploaded onto a Streamlit interactive dashboard allowing users to track and analyse all the available data. 

The scripts are then containerised using Docker and uploaded to an AWS ECR, which allows us to Terraform the dashboard and replicate the scripts. 

## Charts Scripts

The scripts read the data from the centralised RDS database and uses altair, plotly and more data analytics tools to create various visualisations of the energy data. 

## Streamlit scripts

These scripts organise the visualisations, filters and insights on each dashboard page accordingly. This allows for easy navigation across the dashboard by grouping the data analysis by data type and data insights. 

## Usage

### Environment set up

#### Database connection .env

```
DB_NAME={your db name}
DB_USERNAME={your db username}
DB_PASSWORD={your db password}
DB_PORT={your db port}
DB_HOST={your db host}
```

### How to run the dashboard

#### Run locally 

1. Add the environment setup details to your local postgres database in a .env file.
2. Run ```streamlit run dashboard.py``` in the terminal.

#### Run on the cloud

1. Run the dashboard from the ecs tasks public ip address using port 8501 e.g ```{public ip address}:8501```.

