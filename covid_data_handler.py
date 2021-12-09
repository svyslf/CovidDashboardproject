import json
import sched
import time
from typing import Callable
from uk_covid19 import Cov19API

cov_data = {}
# with open("config.json", encoding='utf-8') as json_data_file:
# cov_data = json.load(json_data_file)
# location_data = cov_data.get('location')
# location_type_data = cov_data.get('location_type')


def parse_csv_data(csv_filename) -> list:
    """Reads the csv file provided and formats it into a list of strings
    Arguements:
    csv_filename {csv} - a file containing covid data including the following parameters:
    areaCode,areaName,areaType,date,cumDailyNsoDeathsByDeathDate,
    hospitalCases,newCasesBySpecimenDate

    Returns:
    covid_csv_data {list} - a list of strings containing the above data
    """
    covid_csv_data = []  # declare covid_csv_data as empty list
    # iterates through every line in the csv file, and appends to covid_csv_data
    with open(csv_filename, encoding="utf-8") as csv_file:
        for row in csv_file:
            line = row.split()
            covid_csv_data.append(line)
    return covid_csv_data


def process_covid_csv_data(covid_csv_data: list) -> tuple[int, int, int]:
    """Processes the csv data and returns relevant integer values for selected data.
    Arguement:

    covid_csv_data {list} - a list of strings containing the above data

    Returns:

    tuple {int, int, int} containing:
    last7days_cases {int} - Total cases in the last 7 days as an integer
    hospital_cases {int} - Latest hospital cases value in the csv
    total_deaths {int} - Latest Total deaths value in the csv
    """
    last7days_cases = 0
    for case_position in range(3, 10):
        cases = int("".join(covid_csv_data[case_position]).split(",")[-1])
        last7days_cases += cases
    hospital_cases = int("".join(covid_csv_data[1]).split(",")[-2])
    total_deaths = int("".join(covid_csv_data[14]).split(",")[-3])
    return last7days_cases, hospital_cases, total_deaths


def covid_API_request(location: str = "Exeter", location_type: str = "ltla"):
    """Returns up to date covid data as a dictionary from the public health API
    Arguements:
    location {str} -- the location by which the API will filter data to be requested

    location_type {str} -- the type of location which helps the API filter info further

    Returns:
    data {dict | str} -- A dictionary and string union that contains all the relevant covid info
    for the above arguements
    """
    area_filter = ["areaType=" + location_type, "areaName=" + location]
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases",
    }
    api = Cov19API(filters=area_filter, structure=cases_and_deaths)
    data = api.get_json(save_as="data.json")
    return data


capture_data = covid_API_request()
capture_data_nation = covid_API_request(location="England", location_type="nation")


def local_data_7_days(capture_data: Callable) -> int:
    """Total cases in last 7 days in the local area
    Arguement:

    capture_data {callable} - Takes the value returned from covid_API_request function
    and extracts relevant info

    Returns:

    Integer value with number of total cases
    """
    local_7_days_cases = 0
    for pos, val in enumerate(capture_data["data"], 0):
        if pos in range(1, 8) and val["newCasesBySpecimenDate"] is not None:
            local_7_days_cases += val["newCasesBySpecimenDate"]
    return local_7_days_cases


def national_data_7_days(capture_data_nation: Callable) -> int:
    """Total cases in last 7 days in national area
    Arguement:

    capture_data {callable} - Takes the value returned from the covid_API_request
    function and extracts relevant info

    Returns:

    Integer value with number of total cases
    """
    national_7_days_cases = 0
    for pos, val in enumerate(capture_data_nation["data"], 0):
        if pos > 6:
            break
        if val["newCasesByPublishDate"] is not None:
            national_7_days_cases += val["newCasesByPublishDate"]
    return national_7_days_cases


def data_hospital_cases(capture_data_nation: Callable) -> int:
    """The most updated value of hospital cases in the national context
    Arguement:

    capture_data {callable} - Takes the value returned from the covid_API_request
    function and extracts relevant info

    Returns:

    Integer value with number of total hospital cases
    """
    hospital_cases = 0
    for val in capture_data_nation["data"]:
        if val["hospitalCases"] is not None:
            hospital_cases += val["hospitalCases"]
            break
    return hospital_cases


def data_total_deaths(capture_data_nation: Callable) -> int:
    """The total deaths as per death date in the national area
    Arguement:

    capture_data {callable} - Takes the value returned from the covid_API_request
    function and extracts relevant info

    Returns:

    Integer value with number of total deaths
    """
    death_total = 0
    for val in capture_data_nation["data"]:
        if val["cumDailyNsoDeathsByDeathDate"] is not None:
            death_total += val["cumDailyNsoDeathsByDeathDate"]
            break
    return death_total


covid_final_data = []


def call_all() -> tuple:
    """Calls all functions and outputs value to a tuple
    Returns:

    A tuple containing all relevant data obtained from functions above.

    """
    # print('running')
    covid_final_data = (
        local_data_7_days(capture_data),
        national_data_7_days(capture_data_nation),
        data_hospital_cases(capture_data_nation),
        data_total_deaths(capture_data_nation),
    )
    return covid_final_data


if __name__ == "__main__":
    parse_csv_data(csv_filename="nation_2021-10-28.csv")
    process_covid_csv_data(
        covid_csv_data=parse_csv_data(csv_filename="nation_2021-10-28.csv")
    )
