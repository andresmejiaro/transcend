from requests import post

endpoint = "http://localhost:8000/api/tournament/create/"

data = {
    "name": "Tournament 1",
    "winner": None,
    "start_date": None,
    "end_date": None,
    "matches": []
}

# Replace 'your_csrf_token' with the actual CSRF token
csrf_token = '5v1Qr2It4omiBUI3TSiyOGybJYmUrOO8umt8kVIehcTMHIBYcdxzqTMfXsEwSvr3'

headers = {'X-CSRFToken': csrf_token}

print(f"Sending POST request to {endpoint} with data {data} and headers {headers}")
response = post(endpoint, data=data, headers=headers)


try:
    response_json = response.json()
    print(response_json)
except ValueError:
    print(f"Response does not contain valid JSON. Status code: {response.status_code}, Content: {response.text}")
