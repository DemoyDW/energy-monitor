FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip3 install -r requirements.txt 

COPY load_outages.py . ${LAMBDA_TASK_ROOT}

CMD [ "load_outages.handler" ]




