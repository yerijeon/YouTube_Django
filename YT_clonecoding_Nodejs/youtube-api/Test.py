!pip install google-api-python-client
from apiclient.discovery import build

api_key = '{Your_API_Key}'
youtube = build('youtube', 'v3', developerKey = api_key)

req = youtube.search().list(q='asmr', part='snippet', type='video', maxResults='50')
res = req.execute()