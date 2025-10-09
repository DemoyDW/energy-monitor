# Description

This pipeline automates the process of collecting, cleaning and sorting UK power outage data from the National Grid into a PostgreSQL RDS database. It's an ETL pipeline that extracts live data from a public CSV, transforming it into a structured relational format and loading it into AWS RDS, ready for analysis and visualisation.

The workflow is containerised using Docker and deployed as an AWS Lambda function. This allows for scalable serveless data ingestion without any manual intervention. And this data is then fed directly into the dashboard, powering the various insights for outages across the nation.

## Extract Script
We extract the data from the National Grid website which is in the form of a CSV, then we store it in a tmp local folder (as AWS Lambda can't read local CSVs).

Link used: "https://connecteddata.nationalgrid.co.uk/dataset/d6672e1e-c684-4cea-bb78-c7e5248b62a2/resource/292f788f-4339-455b-8cc0-153e14509d4d/download/power_outage_ext.csv"

## Transform Script
The transform script then takes the information from this CSV then stores them in their relevant tables so they are ready to be uploaded to the postgres RDS database. The tables included:

### Outage Table:
- outage_id
- start_time
- etr
- category_id
- status

### Postcode Table:
- postcode_id
- postcode

### Outage Postcode Link Table
- outage_postcode_link_id
- outage_id
- postcode_id

On top of this we made sure to change the timezone to UK standard time, so we had consistency across the database. Additionally, some values stored in the tables were NaT, so we made sure to change them to None, and this had to be done becasue postgres is unaware of that data type, therefore it will throw an error.

## Load Script

The purpose of the load script is now to pull the other two scripts together and upload the data to RDS. And to do this we made sure to establish the connection to the database. Write the SQL queries to then upload the data. And these functions were all pulled together using an orchestration function. And finally we used a Lambda handler function so it can be called by the Lambda.

# Usage

## Environment set-up

Install the requirements.

```sh
pip3 install -r requirements.txt
```

## Next set up the .env with the required credentials for the RDS

```sh
DB_NAME={"Database name"}
DB_USERNAME={"Username for RDS"}
DB_PASSWORD={"Password for RDS"}
DB_PORT={"Port for the RDS"}
DB_HOST={"RDS address"}
```

# How to run the project

## Run locally 

Run these commands:

```sh
# Build the image
docker buildx build -t outages-lambda .

# Runs the container locally
docker run -p 9000:8080 outages-lambda
```

Switch to a different terminal, then run these commands:

```sh
# Now you can call it just like AWS would, using a POST request with a JSON payload
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d '{}'

# Then add the Lambda runtime endpoint
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
-d '{"url": "https://example.com/outages.csv"}'
```

## Run on the cloud

Run these commands:

```sh
# Authenticate Docker to AWS ECR
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-2.amazonaws.com

# Build and tag
docker build -t outages-lambda .

# Tag for ECR
docker tag outages-lambda:latest <account-id>.dkr.ecr.eu-west-2.amazonaws.com/outages-lambda:latest

# Push to the ECR
docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/outages-lambda:latest
```

Now the pipeline will be up and running on AWS.