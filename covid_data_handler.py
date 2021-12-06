import json
import sched
import time
from typing import Callable
from uk_covid19 import Cov19API



def parse_csv_data(csv_filename) -> list:
    '''reads the csv file provided and formats it into a list of strings'''
    covid_csv_data = []  # declare covid_csv_data as empty list
    # iterates through every line in the csv file, and appends to covid_csv_data
    with open(csv_filename) as csv_file:
        for row in csv_file:
            line = row.split()
            covid_csv_data.append(line)
    return covid_csv_data


def process_covid_csv_data(covid_csv_data):
    ''' takes covid_csv_data as an arguement and returns three relevant variables.'''
    last7days_cases = 0
    for x in range(3, 10):
        cases = int(''.join(covid_csv_data[x]).split(',')[-1])
        last7days_cases += cases
    hospital_cases = int(''.join(covid_csv_data[1]).split(',')[-2])
    total_deaths = int(''.join(covid_csv_data[14]).split(',')[-3])
    return last7days_cases, hospital_cases, total_deaths



def covid_API_request(location="Exeter", location_type="ltla"):
    '''Returns up to date covid data as a dictionary from the public health API

        Arguements:
        location {str} -- the location by which the API will filter data to be requested
        
        location_type {str} -- the type of location which helps the API filter info further
    
        Returns:
        data {dict | str} -- A dictionary and string union that contains all the relevant covid info
        for the above arguements
    '''
    area_filter = [
        'areaType='+location_type,
        'areaName='+location
    ]
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases"
    }
    api = Cov19API(filters=area_filter, structure=cases_and_deaths)
    data = api.get_json()
    return data



def local_data_7_days(capture_data:Callable) -> int:
    '''Total cases in last 7 days in the local area

        Arguement:
        
        capture_data {callable} - Takes the value returned from covid_API_request function 
        and extracts relevant info

        Returns:
        
        Integer value with number of total cases
    '''
    local_7_days_cases = 0
    for pos, val in enumerate(capture_data['data'], 0):
        if pos in range(1, 8) and val["newCasesBySpecimenDate"] != None:
            local_7_days_cases += val["newCasesBySpecimenDate"]
    return local_7_days_cases


def national_data_7_days(capture_data:Callable)-> int:
    '''Total cases in last 7 days in national area
        Arguement:

        capture_data {callable} - Takes the value returned from the covid_API_request
        function and extracts relevant info

        Returns:
        
        Integer value with number of total cases
    '''
    national_7_days_cases = 0
    for pos, val in enumerate(capture_data['data'], 0):
        if pos > 6:
            break
        elif val["newCasesByPublishDate"] is not None:
            national_7_days_cases += val["newCasesByPublishDate"]
    return national_7_days_cases


def data_hospital_cases(capture_data:Callable)-> int:
    '''The most updated value of hospital cases in the national context
        Arguement:
        
        capture_data {callable} - Takes the value returned from the covid_API_request
        function and extracts relevant info

        Returns:
        
        Integer value with number of total hospital cases
    '''
    hospital_cases = 0
    hospital_show = 'Hospital Cases: '
    for val in capture_data['data']:
        if val["hospitalCases"] is not None:
            hospital_cases += val["hospitalCases"]
            break
    return hospital_show + str(hospital_cases)


def data_total_deaths(capture_data:Callable)-> int:
    '''The total deaths as per death date in the national area
        Arguement:
        
        capture_data {callable} - Takes the value returned from the covid_API_request
        function and extracts relevant info

        Returns:
        
        Integer value with number of total deaths
    '''
    death_total = 0
    death_show = 'Total Deaths: '
    for val in capture_data['data']:
        if val["cumDailyNsoDeathsByDeathDate"] != None:
            death_total += val["cumDailyNsoDeathsByDeathDate"]
            break
    return death_show + str(death_total)

covid_final_data = []

def call_all():
    '''Calls all functions and outputs value to a tuple'''
    print('running')
    covid_final_data = (local_data_7_days(capture_data=covid_API_request()),
    national_data_7_days(capture_data=covid_API_request(location='England', location_type='nation')),
    data_hospital_cases(capture_data=covid_API_request(location='England', location_type='nation')),
    data_total_deaths(capture_data=covid_API_request(location='England', location_type='nation')))
    return covid_final_data

s = sched.scheduler(time.time, time.sleep)
def schedule_covid_updates(update_interval:float, update_name:str)-> sched.Event:
    '''Schedules updates to covid data
        Arguements:
        update_interval {float} -- The time at which the update will be executed

        update_name {str} -- The name of the update.

        Returns:
        event {Event} -> The event scheduled by the function
    '''
    event = s.enter(update_interval, 1, call_all, ())
    return event


if __name__ == "__main__":
    parse_csv_data(csv_filename='nation_2021-10-28.csv')
    process_covid_csv_data(covid_csv_data=parse_csv_data(csv_filename='nation_2021-10-28.csv'))
    schedule_covid_updates(10, update_name = 'test')  
    s.run()