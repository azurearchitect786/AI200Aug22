FROM python:3.11-slim
WORKDIR /app

# Install production server dependencies
RUN pip install flask gunicorn

COPY app.py .
EXPOSE 9000

# Use gunicorn to bind securely to all network interfaces on port 9000
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "2", "--timeout", "600", "app:app"]
