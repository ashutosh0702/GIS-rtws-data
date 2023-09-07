FROM public.ecr.aws/lambda/python:3.10

COPY src/geospatial.py ${LAMBDA_TASK_ROOT}
COPY src/lambda_function.py ${LAMBDA_TASK_ROOT}
COPY src/ndvi.py ${LAMBDA_TASK_ROOT}
COPY src/requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir -r requirements.txt

CMD ["lambda_function.lambda_handler"]