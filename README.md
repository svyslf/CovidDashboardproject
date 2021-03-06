# Covid Dashboard project 

## Introduction
Welcome to the smart covid dashboard project. This project aims to inform users of relevant covid data in their area of choice (within the UK). It pulls data from the UK covid-19 API, and displays local and national 7-day infections, hospital cases, and total deaths in the nation chosen. 
The dashboard also displays news data related to covid-19. The data contains news descriptions that the user can then choose to read in detail or remove from their feed. 
Users are also able to schedule regular and repeated updates to covid and news data at their chosen time. 


To get started, we have to do a few things. 
## Prerequisites
Requires Python 3.9.7
    
## Installation
### Setup a virtual environment
1. Create a virtual environment called 'venv' using the following command in your terminal:
    `python3 -m venv venv`
2. Activate it using:   
    `.\venv\scripts\activate`
3. You should see the following:
    `(venv) PS C:\oath\to\project\CovidDashboardproject>` 
4. This means you are in the environment. Here, install the requirements again using:
    `pip install -r requirements.txt` 
5. Handle setuptools dependencies by:
    `pip install -e .`
    This sets up the modules in the virtual environment, allowing them to run. 
Note: Before moving on, you may need to deactivate the virtual environment using: 
    `deactivate`
And then reactivate it (using the command in step 2), to make sure it recognizes all installations. 

    
# Getting Started
## Dashboard Setup
1. You will need an API key from www.Newsapi.org for the news data to appear. 
2. This can be obtained at Newsapi.org > Get API key
3. Register for an API key, and when obtained, input it in the configExample.json file
4. In the config file, you can edit the filter search terms for getting different news info
5. You can also edit location info to get values for different places in the UK.
6. When done with the config file, rename it to config.json. This is important, as the program recognizes a file name config.json only. 
7. Run the program in terminal using:
    `Python -m flaskapp`

## How to use the dashboard
If you have followed the steps correctly, you should see a webpage that looks like this:
![Screenshot (271)](https://user-images.githubusercontent.com/94067614/145304122-a42a5b5f-be1f-4299-8035-5f0e5fbadb67.png)

You can schedule regular and repeated updates to news and covid data. 
1. Input your chosen time
2. Select type of update
3. Click submit
Note: Inputting a time in the past or right now schedules an update for the next day, at that time.

# Testing
To run tests, restart your venv following the steps detailed in the 'NOTE' in Installation.
Then, tests, which are found in the tests folder, will be run by the following command:
    `Pytest`
## Logging
Check the covidlog.log file for a log of all things that go on on the website

### Developer Documentation
Developer documentation can be found at docs/build/html
github - https://github.com/svyslf/CovidDashboardproject
### Details
Author: Vihan Sharma

License: MIT License

Acknowledgements : Matt Collison and Hugo Barbosa


