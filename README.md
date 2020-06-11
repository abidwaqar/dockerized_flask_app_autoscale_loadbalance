# Dockerized flask app with autoscaler and loadbalancer
Auto-scale and Load-balance a dockerized flask app with the help of Flask, HAProxy, Docker and Python

In this project, there is a basic flask app which shows my name and roll number along with id of the docker container in which the app is running. Along with this their is a python script that checks CPU usage and increases increases or decreases the number docker container running accordingly. All the dockers will be running at localhost port 80 in round-robin manner. Every time the page is refreshed the docker is changed and its dockerID is shown on the screen 

Follow the following instructions to run this app:

1. This app will run on ubuntu
2. Install Python, Flask, HAProxy and Docker 
3. Run this command in terminal : ```docker build -t cloud_web_app:latest .```
4. Now run the python script in terminal: ```python autoscale_script.py```
5. Now access HAProxy at localhost port 80
6. **Viola!**