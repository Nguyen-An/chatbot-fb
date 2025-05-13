#Start from the official Python base image.
FROM python:3.12

# Set the working directory within the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /code
COPY ./requirements.txt ./

RUN apt update -y && apt install rustc cargo -y

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . .

ENV HOST 0.0.0.0
EXPOSE 8000
# Run app.py when the container launches
CMD ["fastapi", "run", "app/main.py"]
