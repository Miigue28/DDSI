FROM python:3.12-alpine

ENV FLASK_RUN_HOST=0.0.0.0

# Copy the Python package
COPY ./dist/flaskr-1.0.0-py2.py3-none-any.whl .

# Install the package
RUN pip install --no-cache-dir flaskr-1.0.0-py2.py3-none-any.whl

# Expose the application port
EXPOSE 5000

# Initialize the database
RUN flask --app flaskr init-db

# Run the app
CMD ["flask",  "--app", "flaskr", "run"]
