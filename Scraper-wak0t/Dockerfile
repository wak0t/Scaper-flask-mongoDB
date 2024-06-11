# Use an official Python runtime as a parent image
FROM python:3.12.0

# Set the working directory in the container
WORKDIR /app

# Kopiujemy pliki z zależnościami i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy pozostałe pliki projektu
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["flask", "--app", "app", "run", "--debug", "--host=0.0.0.0"]
