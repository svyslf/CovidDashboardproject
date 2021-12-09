"""The flaskapp module runs the entire program."""
from datetime import datetime, timedelta
import logging
import time
import sched
import json
from typing import Callable
from flask import Flask, render_template, redirect, request, Markup
from covid_data_handler import call_all
from covid_news_handling import news_API_request

FORMAT = "%(levelname)s: %(asctime)s: %(message)s"
logging.basicConfig(filename="covidlog.log", format=FORMAT, level=logging.DEBUG)


s = sched.scheduler(time.time, time.sleep)


def schedule_update(update_interval: float, update_func_name: Callable) -> sched.Event:
    # slightly different implementation than in covid_data_handler, but tests prove it works
    """Schedules updates to covid and news data.

    Arguements:
        update_interval {float} -- The time at which the update will be executed

        update_func_name {callable} -- The function to be called in the scheduler.
        For ex. for a covid update, update_func_name would be = call_all()

    Returns:
        event {Event} -> The event scheduled by the function
    """
    logging.info("queuing update")
    event = s.enter(update_interval, 1, update_func_name, ())
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
    article["content"] = article["description"] + temp

app = Flask(__name__, template_folder="template")


@app.route("/")
def home() -> str:
    """Returns a template with all information at the home page"""
    return render_template(
        "index.html",
        title=Markup("<b>Smart Covid Dashboard</b>"),
        location=Markup(f"<b>{location}</b>"),
        local_7day_infections=display_data[0],
        nation_location=Markup(f"<b>{nation}</b>"),
        national_7day_infections=display_data[1],
        hospital_cases="Hospital cases: " + str(display_data[2]),
        deaths_total="Total deaths: " + str(display_data[3]),
        news_articles=articles[0:4],
        updates=update_list,
        image=image,
        favicon="static/images/favicon.ico",
    )


@app.route("/index", methods=["GET"])
def index():
    s.run(blocking=False)
    return home()

if request.method == 'GET': 
    title_news = request.args.get('notif')
    title_update = request.args.get('update_item')
    time_input =  request.args.get("update")
    label = request.args.get("two")
    repeat = request.args.get("repeat")
    covid_tick = request.args.get("covid-data")
    news_tick = request.args.get("news")
  

    if title_news:
        def index_removes(title_news):
            for pos, val in enumerate(articles):
                if pos < 5 and val["title"] == title_news:
                    articles.pop(pos)
                pos = pos + 1
            return index()

    if title_update:
        def index_removes_updates():
            logging.info("update cancelled")
            for pos, val in enumerate(update_list):
                if pos < 10 and val["title"] == title_update and val["event"] in s.queue:
                    update_list.pop(pos)
                    s.cancel(val["event"])
                pos = pos + 1
            return index()

    if 'update' in request.args.get():
        def time_calc() -> list:
            """Calculates time interval based on current time and time inputted by user
            Returns a list with the time inputted by user and the time interval in:
            - seconds
            - a string of format (%H:%M:%S)
            """
            time_then = datetime.strptime(time_input, "%H:%M")
            current_time = datetime.now()
            c_time_string = str(
                timedelta(hours=current_time.hour, minutes=current_time.minute)
            )
            time_now = datetime.strptime((c_time_string), "%H:%M:%S")
            if time_now < time_then:
                time_interval = time_then - time_now
            else:
                time_interval = timedelta(hours=24) + time_then - time_now
            time_interval_seconds = time_interval.total_seconds()
            return [time_interval_seconds, str(time_interval), time_input]

        extract_time = time_calc()
        repeat_info = ''
        update_list = []
        def dict_creator(event, content_info):
            index_dictionary = {
                "title": label,
                "content": f"{content_info} {extract_time[2]} {repeat_info} ",
                "order": extract_time[0],
                "event": event,
                "rep_event" : False
            }
            update_list.append(index_dictionary)


        if any(val["title"] == label for val in update_list):
            duplicate_name = True

        if duplicate_name:
            # does not allow same-name toasts as they cause deletion errors
            logging.warning("Update name already exists! please pick another name ")
        else:   
            def dict_assembler():
                if news_tick and covid_tick:
                    both = schedule_update(extract_time, call_all) and schedule_update(extract_time, news_API_request)
                    dict_creator(event = both, content_info= 'Covid and news update at')
                if covid_tick:
                    covid_update = schedule_update(extract_time[0], call_all)
                    dict_creator(event = covid_update, content_info='Covid update at')
                elif news_tick:
                    news_update = schedule_update(extract_time[0], news_API_request)
                    dict_creator(event = news_update, content_info= 'News update at')
            update_list = sorted(update_list, key=lambda x: x["order"])
            if repeat:
                repeat_info = 'Repeated'

    for pos, val in enumerate(update_list, 0):
        if val['event'] not in s.queue: 
            if repeat:
                logging.info("This update will be repeated in 24 hours")
                repeat_happens = True

                if val["cov_func"] is not None:
                    val["event"] = schedule_update(
                        extract_time[0] + 86400, val["cov_func"]
                    )
                elif val["news_func"] is not None:
                    val["event"] = schedule_update(
                        extract_time[0] + 86400, val["news_func"]
                    )
                else:  # otherwise, both updates were requested
                    val["event"] = schedule_update(
                        extract_time[0] + 86400, val["cov_func"]
                    ) and schedule_update(extract_time[0] + 86400, val["news_func"])         
        elif val['event'] not in s.queue or repeat_happens is False:
                update_list.pop(pos)
                logging.info("This update has been removed")



    if __name__ == "__main__":
        app.run(debug=True)
