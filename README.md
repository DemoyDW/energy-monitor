# Energy Monitor     

## Description of the project

This project aims to collate data from various sources and present it in an accessible and easily understandable format. 


## usage

The project provides value in three main ways: 

- Power outage email alerts which provide live updates on current power outages.
- Email reports which provide regular summaries on power generation, pricing, demand and carbon intensity .
- An interactive dashboard which provide visualisations on power generation, pricing, power outages and carbon intensity. Also allowing users to sign up for either of the emailing services.

## Environment set up

### Database connection 

```
DB_NAME={your db name}
DB_USERNAME={your db username}
DB_PASSWORD={your db password}
DB_PORT={your db port}
DB_HOST={your db host}
```

### Terraform

```
ACCESS_KEY={your aws access key}
SECRET_KEY={your aws secret access key}
VPC_ID={your vpc id}
VPC_PUBLIC_SUBNET_1={your vpc public subnet 1}
VPC_PUBLIC_SUBNET_2={your vpc public subnet 2}
VPC_PUBLIC_SUBNET_3={your vpc public subnet 3}
REGION={your aws region }
DB_HOST={your db host}
DB_NAME={your db name}
DB_USERNAME={your db username}
DB_PASSWORD={your db password}
DB_PORT={your db port}
```

## How to run the project

### Run locally 

1. Add the environment setup details to a local postgres database in your .env file.
2. Run the files schema.sql then seed.sql on your local database.
3. Run the handler function from load_outages in the outages subdirectory and load_main in the power_readings subdirectory
4. Run the dashboard.py file using streamlit to view the visualisations.

### Run on the cloud

## Architecture
![Architecture diagram](diagrams/architecture_diagram.png)

## ERD
![ERD](diagrams/energy-monitor-erd.png)