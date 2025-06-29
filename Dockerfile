# # Use a Python base image

# FROM python:3.11-slim-bookworm

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements file into the container
# COPY requirements.txt .

# # Install the dependencies
# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code into the container
# COPY . .


# #Create a non-root user and set permissions
# RUN adduser --disabled-password --gecos '' appuser && \
#     chown -R appuser:appuser /app
# USER appuser

# # Expose the port the application will run on
# EXPOSE 8000


# # Set environment variables
# ENV PYTHONUNBUFFERED=1
# ENV FLASK_APP=app.py

# # Run the application
# CMD ["python", "app.py"]



# -------- Stage 1: Build dependencies --------
FROM python:3.11-slim-bookworm as builder

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -------- Stage 2: Final runtime image --------
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

CMD ["python", "app.py"]
