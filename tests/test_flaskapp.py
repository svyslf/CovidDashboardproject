from covid_data_handler import call_all
from flaskapp import schedule_update

def test_schedule_update():
    #test if scheduler can schedule updates
    schedule_update(update_interval=10, update_func_name= call_all)

if __name__ == "__main__":
    try:
        test_schedule_update()
    except AssertionError as message:
        print(message)
