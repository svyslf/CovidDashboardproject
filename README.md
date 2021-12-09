# Covid Dashboard project 

## Introduction
Welcome to the smart covid dashboard project. This project aims to inform users of relevant covid data in their area of choice (within the UK). It pulls data from the UK covid-19 API, and displays 
local and national 7-day infections, and hospital cases and total deaths in the nation chosen. 
The dashboard also displays news data related to covid-19. The data contains news descriptions that the user can then choose to read in detail or remove from their feed. 
Users are also able to schedule regular and repeated updates to covid and news data at their chosen time. 


To get started, we have to do a few things. 
## Prerequisites
Requires Python 3.9.7

## Installation
To install all required modules, enter the following command in your terminal:
    pip install -r requirements.txt

# Getting Started
### Dashboard Setup
1. You will need an API key from Newsapi.org for the news data to appear. 
2. This can be obtained at Newsapi.org > Get API key
3. Register for an API key, and when obtained, input it in the configExample.json file
4. In the config file, you can also edit the location to get values for different places in the UK.
5. When done with the config file, rename it to config.json. This is important.
6. Run the module called Flaskapp using the following command (or by using the run feature in your code editor):
    Python -m flaskapp
 
### How to use the dashboard
If you have followed the steps correctly, you should see a webpage that looks like this:
![Screenshot (271)](https://user-images.githubusercontent.com/94067614/145304122-a42a5b5f-be1f-4299-8035-5f0e5fbadb67.png)


