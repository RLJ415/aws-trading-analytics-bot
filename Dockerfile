FROM public.ecr.aws/lambda/python:3.14

COPY requirements.txt ${LAMBDA_TASK_ROOT}/

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ${LAMBDA_TASK_ROOT}/src/

COPY watchlist.txt ${LAMBDA_TASK_ROOT}/watchlist.txt

CMD ["src.lambda_handler.lambda_handler"]