#Base image of python for Lambda
FROM public.ecr.aws/lambda/python:latest

#Set the default directory
WORKDIR ${LAMBDA_TASK_ROOT}

#Copy over requirements
COPY requirements.txt .

#Install all requirements on the container
RUN pip3 install -r requirements.txt 

#Copy over outage ETL files
COPY load_outages.py . ${LAMBDA_TASK_ROOT}

#Run the ETL pipeline
CMD [ "load_outages.handler" ]




