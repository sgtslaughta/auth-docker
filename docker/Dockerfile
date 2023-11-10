# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY python/ /app

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

# Install Streamlit and Streamlit-Elements
RUN pip3 install streamlit streamlit-elements

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["streamlit", "run", "/app/app.py", "--browser.gatherUsageStats",
"false", "--server.port", "8080"]
