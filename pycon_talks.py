#! /usr/bin/python3
# get the talks information for pycon2018
# get_data return a array of dict
#
import datetime
import requests
from bs4 import BeautifulSoup


def clean_text(text):
    return text.strip('\t\r\n ').replace('\n', '')


def date_range(start_date, end_date, step=1, **kwargs):
    start = start_date
    # the range include the end date
    # change "<=" to "<" if you want the same behavior of the range function
    while start <= end_date:
        yield start
        start += datetime.timedelta(days=step)


def get_time(time):
    if time.lower() == 'noon':
        time = datetime.time(12, 0)
    else:
        time_format = "%I:%M %p" if ":" in time else "%I %p"
        time = datetime.datetime.strptime(time, time_format).time()
    return time


def get_schedule(info):
    schedule = list(map(clean_text, info.strip("\n ").split("\n")))
    day_name = schedule[0]
    time_str = schedule[1].replace(".", "")
    room = schedule[3]
    date = WEEK_DAYS[day_name]
    start, end = time_str.split("–")
    start_time = get_time(start)
    end_time = get_time(end)
    start_date = datetime.datetime.combine(date, start_time)
    end_date = datetime.datetime.combine(date, end_time)
    result = {
        'start_date': start_date,
        'end_date': end_date,
        'duration': int((end_date - start_date).seconds/60),
        'room': room
    }
    return result


def get_data():
    response = requests.get(EVENT_INFO['url'])
    soup = BeautifulSoup(response.content, 'html.parser')
    data = []
    for i, header in enumerate(soup.find_all('h2')):
        a_tag = list(header.find_all('a'))[0]
        talk_id = a_tag.get('id')
        url = a_tag.get('href')
        p1 = header.find_next_sibling('p')
        talk_data = list(p1.find_all('b'))
        title = clean_text(header.text)
        talkers = clean_text(talk_data[0].text)
        schedule = get_schedule(talk_data[1].text)
        p2 = p1.find_next_sibling('div').text
        description = clean_text(p2)
        talk = {
            'id': talk_id,
            'title': title,
            'url': url,
            'talker': talkers,
            'schedule': schedule,
            'description': description
        }
        data.append(talk)
    return data

##############################################################

EVENT_INFO = {
    'url': "https://us.pycon.org/2018/schedule/talks/list",
    'start_date': datetime.date(2018, 5, 8),
    'end_date': datetime.date(2018, 5, 13)
}
#creating a dict with the name of the week day, to map dayname with date
# i.e. {Saturday: datetime(2018, 05, 12)}
WEEK_DAYS = {d.strftime("%A"): d for d in date_range(**EVENT_INFO)}
data = get_data()
print("{0} talks".format(len(data)))
