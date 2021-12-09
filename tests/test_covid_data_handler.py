from covid_data_handler import *

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_local_data_7_days():
    # test if function will skip null or none values and return valid info
    # it should return the sum of all valid data, which in this case will be just 21
    test_case_7_day = local_data_7_days({ "data": [{
            "date": "2021-12-08",
            "areaName": "Exeter",
            "newCasesByPublishDate": 93,
            "newCasesBySpecimenDate": None,
            "cumDailyNsoDeathsByDeathDate": None,
            "hospitalCases": None
        },
        {
            "date": "2021-12-07",
            "areaName": "Exeter",
            "newCasesByPublishDate": 133,
            "newCasesBySpecimenDate": 21,
            "cumDailyNsoDeathsByDeathDate": None,
            "hospitalCases": None
        }]})
    assert test_case_7_day == 21
    assert isinstance(test_case_7_day, int) 

def test_national_data_7_days():
    # test if function will skip null or none values and return valid info
    # it should return the sum of all valid data, which in this case will be 226 (no none values)
    test_case_7_day_national = national_data_7_days({ "data": [{
            "date": "2021-12-08",
            "areaName": "Exeter",
            "newCasesByPublishDate": 93,
            "newCasesBySpecimenDate": None,
            "cumDailyNsoDeathsByDeathDate": None,
            "hospitalCases": None
        },
        {
            "date": "2021-12-07",
            "areaName": "Exeter",
            "newCasesByPublishDate": 133,
            "newCasesBySpecimenDate": 21,
            "cumDailyNsoDeathsByDeathDate": None,
            "hospitalCases": None
        }]})
    assert test_case_7_day_national == 226
    assert isinstance(test_case_7_day_national, int) 

def test_data_hospital_cases():
    # test if function will skip null or none values and return valid info
    # it should return the latest no. of hospital cases
    test_hospital_case_data = data_hospital_cases({ "data": [{
            "date": "2021-12-08",
            "areaName": "Exeter",
            "newCasesByPublishDate": 93,
            "newCasesBySpecimenDate": None,
            "cumDailyNsoDeathsByDeathDate": None,
            "hospitalCases":  6053
        },
        {
            "date": "2021-12-07",
            "areaName": "Exeter",
            "newCasesByPublishDate": 133,
            "newCasesBySpecimenDate": 21,
            "cumDailyNsoDeathsByDeathDate": None,
            "hospitalCases": 6027
        }]})
    assert test_hospital_case_data == 6053
    assert isinstance(test_hospital_case_data, int) 

def test_total_deaths():
    # test if function will skip null or none values and return valid info
    # it should return the latest valid no. of total deaths
    test_total_death_data = data_total_deaths({ "data": [{
            "date": "2021-12-08",
            "areaName": "Exeter",
            "newCasesByPublishDate": 93,
            "newCasesBySpecimenDate": None,
            "cumDailyNsoDeathsByDeathDate": None,
            "hospitalCases":  6053
        },
        {
            "date": "2021-12-07",
            "areaName": "Exeter",
            "newCasesByPublishDate": 133,
            "newCasesBySpecimenDate": 21,
            "cumDailyNsoDeathsByDeathDate": 146563,
            "hospitalCases": 6027
        }]})
    assert test_total_death_data == 146563
    assert isinstance(test_total_death_data, int) 

def test_call_all():
    covid_final_data_test = call_all()
    assert isinstance(covid_final_data_test, (tuple))

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')



