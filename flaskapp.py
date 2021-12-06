from datetime import datetime, timedelta
import time
import sched
import json
from typing import Callable
from flask import Flask, render_template, redirect, request, Markup
from covid_data_handler import call_all
from covid_news_handling import news_API_request

s = sched.scheduler(time.time, time.sleep)
def schedule_update(update_interval:float, update_name:Callable) -> sched.Event:
    ''' Schedules updates to covid and news data.

        Arguements:
            update_interval {float} -- The time at which the update will be executed

            update_name {callable} -- The function to be called in the scheduler. 
            For ex. for a covid update, update_name would be = call_all()

        Returns:
            event {Event} -> The event scheduled by the function
    '''
    event = s.enter(update_interval, 1, update_name, ())
    return event

display_data = call_all()                                           
update_list = []
articles = news_API_request(covid_terms="Covid COVID-19 coronavirus")


config_data = {}
with open("config.json", encoding= 'utf-8') as json_data_file:
    config_data = json.load(json_data_file)
nation = config_data.get('nation')
location = config_data.get('location')
image = config_data.get('image')

for article in articles:
    temp = Markup(f'<a href ={article["url"]}> Read More...</a>')
    article['content'] = article['description'] + temp

app = Flask(__name__, template_folder='template')
@app.route("/")
def home():
    ''' Returns a template with all information at the home page'''
    s.run(blocking=False)
    return render_template('index.html', title=Markup('<b>Smart Covid Dashboard</b>'),
        location=Markup(f'<b>{location}</b>'),
        local_7day_infections=display_data[0],
        nation_location=Markup(f'<b>{nation}</b>'),
        national_7day_infections=display_data[1],
        hospital_cases=display_data[2],
        deaths_total=display_data[3],
        news_articles=articles[0:4],
        updates=update_list, 
        image = image, 
        favicon = 'static/images/favicon.ico')

@app.route("/index", methods=["GET"])
def index():
    ''' Takes user inputs and computes appropriate response '''
    s.run(blocking=False)

    repeat_check = False
    duplicate_name = False  
    repeat = bool(request.args.get('repeat'))
    news_tick = request.args.get('news')
    covid_tick = request.args.get('covid-data')
    label = request.args.get('two')

    if 'notif' in request.args:
        title = request.args.get('notif')
        for pos, val in enumerate(articles):
            if pos < 5 and val['title'] == title:
                articles.pop(pos)
            pos = pos + 1

    if 'update' in request.args:
        global extract_time, update_list    #Global declaration used to avoid unbound variables further down the program 

        def time_calc(): 
            ''' Calculates time interval based on current time and time inputted by user
                Returns a list with the time inputted by user and the time interval in:
                - seconds
                - a string of format (%H:%M:%S)
            '''
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

        time_until_update_popup = Markup(f'<span class="badge badge-dark"> (in {extract_time[1]}) </span>')
        def toast_content_creator(content_info: str, event: sched.Event, func1=None, func2=None) -> dict:
            ''' Creates all information to be displayed on toasts on webpage.
                Easily modifiable based on user-input. 

                Arguements:
                    content_info {str} -- The content information that is displayed on the webpage.
                    
                    event {event} -- Event information used to identify which toast cancels which event
                    
                    func1 and func2 {callable} -- The functions (None by default) that the scheduler calls when scheduling events

                Returns:
                     A dictionary containing user input and event information
            '''
            index_dictionary = {'title': label, 
            'content': f'{repeat_info} {content_info} {extract_time[2]} ' + time_until_update_popup, 
            'order' : extract_time[0], 
            'event': event, 
            'function1': func1,
            'function2':func2}
            return index_dictionary

        if any(val['title'] == label for val in update_list):
            duplicate_name = True

        if duplicate_name:
            print('name already exists! please pick another name ')
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
                update_list.append(toast_content_creator(content_info='News update at', event = news_event, func2 = call_all))
            update_list = sorted(update_list, key=lambda x: x['order']) #sort list in by increasing time interval

    for pos, val in enumerate(update_list):
        if val['event'] not in s.queue:
            if repeat_check:
                if val['function2'] is None:
                    rep_covid_event = schedule_update(extract_time[0], val['function1'])
                    repeat_check = False
                    val['event'] = rep_covid_event   
                elif val['function1'] is None:
                    rep_news_event = schedule_update(extract_time[0], val['function2'])
                    val['event'] = rep_news_event
                    repeat_check = False
                else:
                    rep_both_events = schedule_update(extract_time[0], val['function1']) and schedule_update(extract_time[0], val['function2'])
                    val['event'] = rep_both_events
                    repeat_check = False
            else:
                update_list.pop(pos)

    if 'update_item' in request.args:
        title = request.args.get('update_item')
        for pos, val in enumerate(update_list):
            if pos < 10 and val['title'] == title and val['event'] in s.queue:
                update_list.pop(pos)
                s.cancel(val['event'])
            pos = pos + 1 
            
    return redirect('/', 302)
if __name__ == "__main__":
    app.run(debug=True)
    
