import json
import sched
import time
import requests

data = {}
with open("config.json", encoding="utf-8") as json_data_file:
    data = json.load(json_data_file)
    covid_terms_json = data.get("covid_terms")


def news_API_request(covid_terms=covid_terms_json):
    """Requests news data from newsapi.org to be displayed on the webpage in the flaskapp
    Arguements:
    covid_terms {str} - A string of relevant keywords which act as keywords to filter news articles
    Returns:
    A list of dictionaries containing relevant article information
    """
    base_url = "https://newsapi.org/v2/everything?"
    api_key = "7ead3967d6264d4abcfbbae5bb65ea4d"  # data.get("apiKey")
    finalized_url = base_url + "q=" + covid_terms + "&apiKey=" + api_key
    response = requests.get(finalized_url).json()
    articles = response["articles"]
    return articles


news_API_request()

s = sched.scheduler(time.time, time.sleep)


def update_news(update_name="default") -> tuple[sched.Event, str]:
    """Schedules updates to news data
    Arguements:
    update_interval {float} -- The time at which the update will be executed

    update_name {str} -- The name of the update.

    Returns:
    event {Event} -> The event scheduled by the function
    """
    event = s.enter(1, 1, news_API_request, ())
    return event, update_name


update_news()
