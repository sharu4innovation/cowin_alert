

import json
import requests
import datetime
from datetime import timedelta
import schedule 
import time 

def check_availability():
    
    WEBHOOK_URL = "https://hooks.slack.com/services/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"
    WEBHOOK_URL_PUBLIC = "https://hooks.slack.com/services/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"
    COWIN_WEB_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=294"


    date = datetime.datetime.today()
    date = date.strftime('%d-%m-%Y')
    

    COWIN_WEB_URL = COWIN_WEB_URL + f"&date={date}"

    request_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    response = requests.get(COWIN_WEB_URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
    data = response.json()

    print(len(data['centers']))

    available_centers = []
    for center in data['centers']:
        
        sessions = center['sessions']
        record = {k:v for k,v in center.items() if k in ['name', 'pincode','address']}
        record['sessions'] = []
        available = False
        for session in sessions:
            if session['min_age_limit'] == 18 and session['available_capacity'] > 0:
                available = True
                session_info = {k:v for k,v in session.items() if k in ['min_age_limit', 'date', 'vaccine', 'available_capacity']}
                record['sessions'].append(session_info)
        if available:
            available_centers.append(record)


    if len(available_centers) > 0:
        slack_message = available_centers
        slack_message = {'text': json.dumps(slack_message, indent=2)}
        slack_message = json.dumps(slack_message)

        response = requests.post(
            WEBHOOK_URL, slack_message,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
        )

        response = requests.post(
            WEBHOOK_URL_PUBLIC, slack_message,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
        )

        print(f"checked availablity at {request_time}: {len(available_centers)}")
    else:
        print(f"checked availablity at {request_time}: None")

schedule.every(0.25).minutes.do(check_availability)

while True:
    schedule.run_pending()
    time.sleep(0.25)


# check_availability()