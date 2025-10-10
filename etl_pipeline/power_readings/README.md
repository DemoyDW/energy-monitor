# Description

The power_reading folder contains all the scripts required to build and run the power readings pipeline. This pipeline gathers data from multiple sources, including NESO for carbon intensity data and ELEXON for pricing, demand, power, and energy generation information.

There are two separate extract scripts, each responsible for retrieving data from different API endpoints. The transformation logic is organised into two files, tailored to transform each dataset for database insertion.

The folder also includes three load files: two are responsible for loading data into the RDS, and the third is the main file that runs the entire ETL process through a handler function.

This pipeline is scheduled to run every 30 minutes, in alignment with the UK energy market’s half-hour settlement periods. On each trigger, the ETL process extracts, transforms, and loads the latest data into the RDS database.


# Usage

## Requirements
A .env folder with the following details
``` sh
DB_NAME={"Database name"}
DB_USERNAME={"Username for RDS"}
DB_PASSWORD={"Password for RDS"}
DB_PORT={"Port for the RDS"}
DB_HOST={"RDS address"}
```

## To install all the dependencies needed run the following

``` sh
pip install -r requirements.txt
```

## How to run the dockerised script locally

- Build the container
```sh
docker build -t {NAME} .
```

- Run locally
``` sh
docker run -p 9000:8080 --env-file .env image_name
```

- Open another terminal
``` sh
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```


## Run on the cloud
- Authenticate Docker to AWS ECR
```sh
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-2.amazonaws.com
```


- Build and tag
```
docker build -t power_reading-lambda .
```

- Tag for ECR
```
docker tag power_reading-lambda:latest <account-id>.dkr.ecr.eu-west-2.amazonaws.com/power_reading-lambda:latest
```

- Push to the ECR
```
docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/power_reading-lambda:latest
```