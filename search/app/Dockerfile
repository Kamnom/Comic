# start by pulling the python image
FROM python:3.9-alpine3.16


RUN /usr/local/bin/python -m pip install --upgrade pip


# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app


RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT ["python"]

CMD ["app.py" ]