from datetime import datetime, timedelta
import logging
import time
import sched
import json
from typing import Callable, Any
from flask import Flask, render_template, redirect, request, Markup
from covid_data_handler import call_all, schedule_covid_updates
from covid_news_handling import news_API_request

FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(filename="covidlog.log", format=FORMAT, level=logging.DEBUG)


s = sched.scheduler(time.time, time.sleep)
def schedule_update(update_interval:float, update_func_name:Callable) -> sched.Event:
    #slightly different implementation than in covid_data_handler, but tests prove it works
    """ Schedules updates to covid and news data.

        Arguements:
            update_interval {float} -- The time at which the update will be executed

            update_func_name {callable} -- The function to be called in the scheduler.
            For ex. for a covid update, update_func_name would be = call_all()

        Returns:
            event {Event} -> The event scheduled by the function
    """
    logging.info('queuing update')
    event = s.enter(update_interval, 1, update_func_name, ())
    return event

display_data = call_all()
update_list = []
articles = news_API_request(covid_terms="Covid COVID-19 coronavirus")
config_data = {}

#with open("config.json", encoding= 'utf-8') as json_data_file:
#    config_data = json.load(json_data_file)
#nation = config_data.get('nation')
#location = config_data.get('location')
#image = config_data.get('image')

for article in articles:
    temp = Markup(f'<a href ={article["url"]}> Read More...</a>')
    article['content'] = article['description'] + temp

app = Flask(__name__, template_folder='template')
@app.route("/")
def home() -> str:
    """ Returns a template with all information at the home page """
    s.run(blocking=False)
    return render_template('index.html', title=Markup('<b>Smart Covid Dashboard</b>'),
        location=Markup(f'<b>Exeter</b>'),
        local_7day_infections=display_data[0],
        nation_location=Markup(f'<b>England</b>'),
        national_7day_infections=display_data[1],
        hospital_cases='Hospital cases: ' + str(display_data[2]),
        deaths_total='Total deaths: ' + str(display_data[3]),
        news_articles=articles[0:4],
        updates=update_list,
        image = 'dowwn.jpg',
        favicon = 'static/images/favicon.ico')

@app.route("/index", methods=["GET"])
def index():
    """ Takes user inputs and computes appropriate response """
    #Global declaration used to avoid unbound variables further down the program
    global update_list, extract_time, duplicate_name, repeat_check
    
    s.run(blocking=False)
    duplicate_name = False
    
    if 'notif' in request.args:
        title = request.args.get('notif')
        for pos, val in enumerate(articles):
            if pos < 5 and val['title'] == title:
                articles.pop(pos)
            pos = pos + 1

    if 'update_item' in request.args:                      #removes update toast when cross is clicked
        title = request.args.get('update_item')
        logging.info('update cancelled')
        for pos, val in enumerate(update_list):
            if pos < 10 and val['title'] == title and val['event'] in s.queue:
                update_list.pop(pos)
                s.cancel(val['event'])
            pos = pos + 1

    if 'update' in request.args:
        def time_calc() -> list:
            """ Calculates time interval based on current time and time inputted by user
                Returns a list with the time inputted by user and the time interval in:
                - seconds
                - a string of format (%H:%M:%S)
            """ 
            time_input = request.args.get('update')                          
            time_then = datetime.strptime(time_input, "%H:%M")
            current_time = datetime.now()
            c_time_string = str(timedelta(hours = current_time.hour, minutes = current_time.minute))
            time_now = datetime.strptime((c_time_string), "%H:%M:%S")
            if time_now < time_then:
                time_interval = time_then - time_now
            else:
                time_interval = timedelta(hours=24) + time_then - time_now
            time_interval_seconds = time_interval.total_seconds()
            return [time_interval_seconds, str(time_interval), time_input]

        extract_time = time_calc()
        label = request.args.get('two')
        repeat = request.args.get('repeat')
        covid_tick = request.args.get('covid-data')
        news_tick = request.args.get('news')

        def toast_content_creator(content_info:str, event: sched.Event, func1= None, func2= None) -> dict[str, Any]:
            """ Creates all information to be displayed on toasts on webpage.
                Easily modifiable based on user-input.

                Arguements:
                    content_info {str} -- The content information that is displayed on the webpage.

                    event {event} -- Event information used to identify which toast cancels which event

                    func1 and func2 {callable} -- The functions (None by default) that the scheduler calls when scheduling events

                Returns:
                    index_dictionary {dict[str, any]} -- A dictionary containing user inputs and event information
            """
            time_until_update_popup = Markup(f'<span class="badge badge-dark"> (in {extract_time[1]}) </span>')
            index_dictionary = {'title': label,
            'content': f'{repeat_info} {content_info} {extract_time[2]} ' + time_until_update_popup,
            'order' : extract_time[0],
            'event': event,
            'cov_func': func1,
            'news_func': func2}
            return index_dictionary

        if any(val['title'] == label for val in update_list):
            duplicate_name = True

        if duplicate_name:
            #does not allow same-name toasts as they cause deletion errors
            logging.warning('Update name already exists! please pick another name ')
        else:
            if repeat:
                repeat_info = 'Repeated'
                repeat_check = True
            else:
                repeat_info = ''
            if covid_tick and news_tick:
                both_events = schedule_update(extract_time[0], call_all) and schedule_update(extract_time[0], news_API_request)
                update_list.append(toast_content_creator(content_info='Covid and News update at', event = both_events, func1 = call_all, func2 = news_API_request))
            elif covid_tick:
                covid_event = schedule_update(extract_time[0], call_all)
                update_list.append(toast_content_creator(content_info='Covid update at', event = covid_event, func1 = call_all))
            elif news_tick:
                news_event = schedule_update(extract_time[0], news_API_request)
                update_list.append(toast_content_creator(content_info='News update at', event = news_event, func2 = news_API_request))
            update_list = sorted(update_list, key=lambda x: x['order']) #sort list in by increasing time interval

    for pos, val in enumerate(update_list):
        #For toasts in update_list, remove toasts with finished events if they are NOT repeated.
        if val['event'] not in s.queue:
            if repeat_check:
                logging.info('This update will be repeated in 24 hours')
                repeat_check = False
                if val['cov_func'] is not None:               
                    val['event'] = schedule_update(extract_time[0]+86400, val['cov_func'])
                elif val['news_func'] is not None:              
                    val['event'] = schedule_update(extract_time[0]+86400, val['news_func'])   
                else:                                     #otherwise, both updates were requested
                    val['event'] = schedule_update(extract_time[0]+86400, val['cov_func']) and schedule_update(extract_time[0]+86400, val['news_func'])
            else:
                update_list.pop(pos)                       #remove update by position in update_list
    return redirect('/', 302)

if __name__ == "__main__":
    app.run(debug=True)

