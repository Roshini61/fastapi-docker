# <<<<<<< HEAD
# # Use the official Python image as base image
# FROM python:3

# # Set the working directory in the container
# WORKDIR /app

# # Copy the local main.py file to the container
# COPY main.py .

# # Run the Python script when the container launches
# CMD ["python", "main.py"]
# =======
# # Use Python 3.9 base image
# FROM python:3.9

# # Set working directory
# WORKDIR /app

# # Copy your Python script
# COPY main.py .

# # Run the Python script
# CMD ["python", "main.py"]
# >>>>>>> bea78a9a828f56a33e1ca7b499de2ba4514d6511
FROM python

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
