from covid_data_handler import call_all
from flaskapp import schedule_update, time_calc

def test_time_calc():
    #Test if the time calculated in seconds is returned as float value
    #This is important since scheduler excepts float time-intervals
    
    test_extract = time_calc(time_input='00:00')
    assert isinstance(test_extract[0], float), 'time_calc does not return float' 

def test_schedule_update():
    #test if scheduler can schedule updates
    schedule_update(update_interval=10, update_func_name= call_all)

if __name__ == "__main__":
    
    try:
        test_time_calc()
        test_schedule_update()
    except AssertionError as message:
        print(message)
