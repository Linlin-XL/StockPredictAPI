ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8
ARG PYTHON_VERSION=3.9.8

FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT} AS py3
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}

RUN apt-get update && apt-get -y install rsync

COPY --from=py3 / /

ARG PYSPARK_VERSION=3.3.1
RUN pip --no-cache-dir install pyspark==${PYSPARK_VERSION}

# set working directory
WORKDIR /app

# Copy the rest of the project files to the container
COPY . .

# install dependencies
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
