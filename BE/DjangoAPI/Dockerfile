# Use the official Python image with tag 3.8-slim
FROM python:3.8-slim

# Set environment variables to optimize Python for Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory within the container to /app/
WORKDIR /app/

# Install virtualenv
RUN pip install --upgrade pip && pip install virtualenv

# Create a virtual environment and activate it
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN /venv/bin/pip install --upgrade pip

# Copy the requirements.txt file to /app/
COPY requirements.txt /app/

# Install project dependencies within the virtual environment
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the entire project to /app/
COPY . /app/

# Run migrations and start the Django development server
CMD ["sh", "-c", "/venv/bin/python ./BE/DjangoAPI/manage.py makemigrations && /venv/bin/python ./BE/DjangoAPI/manage.py migrate && /venv/bin/python ./BE/DjangoAPI/manage.py runserver 0.0.0.0:8000"]