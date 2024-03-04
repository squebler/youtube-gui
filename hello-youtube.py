from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
from requests import HTTPError

# Define the scopes
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

# Create the flow using the client_secrets.json file
client_secrets_file = 'client_secret.json'
flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes=scopes)

# Prompt the user to authorize by opening a browser window.
# The method will start a local server to listen for the authentication token.
# If you encounter issues with the default port, you can specify it using the `port` argument
credentials = flow.run_local_server(open_browser=True)

# Build the YouTube client
youtube = build('youtube','v3',credentials=credentials)

# Make your request
resultsPerPage = 1000
request = youtube.playlists().list(
    part="snippet,contentDetails",
    mine=True,
    maxResults=resultsPerPage
)

try:
    response = request.execute()
except HTTPError as e:
    print('Error response status code : {0}, reason : {1}'.format(e.status_code, e.error_details))

# Get the info from the response, which is a dictionary
# response_as_json = json.dumps(response, indent=4)
#print(response_as_json)

i = 1
for playlist in response["items"]:
    print(f"{i}: {playlist["snippet"]["title"]}")
    i+=1

# "nextPageToken": "CAUQAA",
# "pageInfo": {
#     "totalResults": 292,
#     "resultsPerPage": 5
# }
    
nextPageToken = response["nextPageToken"]
# if nextPageToken:
#     print(f"nextPageToken: {nextPageToken}")
totalResults = response['pageInfo']['totalResults']
# print(f"totalResults: {totalResults}")
resultsPerPage = response['pageInfo']['resultsPerPage']
# print(f"resultsPerPage: {resultsPerPage}")

# so, this will work; but YT doesn't actually give you all the playlists;
# it doesn't give you the built-in ones: Watch Later, Likes, Favorites, Uploaded;
# I'm not sure I have the names of those lists correct; the API might have different names
while request := youtube.playlists().list_next(previous_request=request, previous_response=response):
    try:
        response = request.execute()
    except HTTPError as e:
        print('Error response status code : {0}, reason : {1}'.format(e.status_code, e.error_details))
    
    for playlist in response["items"]:
        print(f"{i}: {playlist["snippet"]["title"]}")
        i+=1


