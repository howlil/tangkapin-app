FROM python:3.12-slim

# Set the working directory
WORKDIR /app
COPY /app .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
ENV PORT=3000
EXPOSE 3000

# Run the application
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:3000", "--workers", "4", "--threads", "8"]
