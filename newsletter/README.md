# Description 

The newsletter folder contains several scripts that connect to the database and retrieve relevant weekly summary data. This data is then used to generate a HTML email containing all the key insights, which is sent to subscribed members.

The folder also includes a Dockerfile that packages the newsletter functionality into a container. This container is pushed to AWS ECR and used in an AWS Step Function as a Lambda function. The Lambda is responsible for sending bulk emails to all subscribers via Amazon SES.

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
docker build -t newsletter-lambda .
```

- Tag for ECR
```
docker tag newsletter-lambda:latest <account-id>.dkr.ecr.eu-west-2.amazonaws.com/newsletter-lambda:latest
```

- Push to the ECR
```
docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/newsletter-lambda:latest
```