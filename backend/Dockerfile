# Stage 1: Compile contracts
FROM python:3.10.4 AS builder

WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory to the container
COPY . /app

# Run brownie compile
RUN brownie compile

# Stage 2: Final image
FROM python:3.10.4

WORKDIR /app

# Set the PYTHONPATH to /app
ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV BROWNIEPATH="/app:${BROWNIEPATH}"

# Copy the compiled contracts from the builder stage to the final image
COPY --from=builder /app /app

# Copy the rest of the project files to the final image
COPY . /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your app
CMD ["python", "/app/api/api.py"]
