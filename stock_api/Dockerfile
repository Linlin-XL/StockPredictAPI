# pull official base image
FROM python:3.9
RUN apt-get update && apt-get install -y postgresql-client

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set working directory
WORKDIR /app

# Copy the rest of the project files to the container
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=stock_api.settings

# Expose port 8000
EXPOSE 8000

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

# start app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
