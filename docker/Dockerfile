# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Make the /app inside the container if it doesn't exist
RUN mkdir -p /app

# Copy the current directory contents into the container at /app
COPY python/ /app

# Make port 8080 available to the world outside this container
EXPOSE 8088

# Install any needed packages specified in requirements.txt
# Uncomment the line below if you have a requirements.txt file
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r /app/requirements.txt

# Install Streamlit and other required packages
RUN pip install streamlit requests pandas plotly-express

# Display contents of /app
CMD ["ls", "-lisa", "/app"]

# Run Connect.py when the container launches
CMD ["streamlit", "run", "/app/Connect.py", "--browser.gatherUsageStats=false", "--server.port=8088"]
