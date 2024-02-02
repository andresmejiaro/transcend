# utils/url_macros.py

# API_BASE_URL = 'http://localhost:8000/api'
# WS_BASE_URL = 'ws://localhost:8001/ws'

API_BASE_URL = 'https://c3r1s1.42madrid.com:3000/api'
WS_BASE_URL = 'wss://c3r1s1.42madrid.com:3000/ws'

# WS Templates
LOBBY_URI_TEMPLATE = WS_BASE_URL + '/lobby/?token={token}'
PONG_URI_TEMPLATE = WS_BASE_URL + '/pong2/{match_id}/?token={token}'

# API Endpoints
LOGIN = API_BASE_URL + '/user/login/'
REGISTER = API_BASE_URL + '/user/signup/'
GET_CLIENT_ID = API_BASE_URL + '/get_user_id/{username}/'
GET_CLIENT_INFO = API_BASE_URL + '/user/info-me/{username}/'
GET_LIST_FRIENDS = API_BASE_URL + '/user/{client_id}/friendlist/'
ADD_FRIEND = API_BASE_URL + '/user/{client_id}/addfriend/'
REMOVE_FRIEND = API_BASE_URL + '/user/{client_id}/removefriend/'
GET_USER_STATS = API_BASE_URL + '/user/{client_id}/stats/'

