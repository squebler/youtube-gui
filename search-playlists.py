from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import os
from requests import HTTPError
import tkinter as tk


def getFakeResponseFileName(iResponse):
    return f"fakeResponse{iResponse}.json"


def deleteFakeResponses():
    iResponse = 0    
    while os.path.exists(fakeResponseFileName := getFakeResponseFileName(iResponse)):
        os.remove(fakeResponseFileName)
        iResponse += 1


def saveFakeResponse(response, iResponse):
    if mode == "fake":
        return

    if iResponse == 0:
        deleteFakeResponses()
    
    responseJson = json.dumps(response, indent=4)
    with open(getFakeResponseFileName(iResponse),'w') as fakeResponseFile:
        fakeResponseFile.write(responseJson)


def getFakeResponse(iResponse):
    fakeResponseFileName = getFakeResponseFileName(iResponse)
    if not os.path.exists(fakeResponseFileName):
        return None
    with open(fakeResponseFileName,'r') as fakeResponseFile:
        fakeResponseJson = fakeResponseFile.read()
        fakeResponse = json.loads(fakeResponseJson)
        return fakeResponse


def executeRequest(request, iResponse):
    if mode == "fake":
        return getFakeResponse(iResponse)
    try:
        response = request.execute()
    except HTTPError as e:
        print('Error response status code : {0}, reason : {1}'.format(e.status_code, e.error_details))
        raise
    saveFakeResponse(response, iResponse)
    return response


def initialize():

    def buildPlaylistsFirstPageRequest():
        if mode == "fake":
            return None, None

        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes=scopes)
        credentials = flow.run_local_server(open_browser=True)

        youtube = build('youtube','v3',credentials=credentials)


        resultsPerPage = 1000
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=resultsPerPage
        )
        return request, youtube
    
    request, youtube = buildPlaylistsFirstPageRequest()

    iResponse = -1
    response = executeRequest(request, iResponse := iResponse + 1)

    i = 1
    for playlist in response["items"]:
        title = playlist['snippet']['title']
        url = f"https://www.youtube.com/playlist?list={playlist['id']}"
        playlists.append(f"{title}\n{url}")
        print(f"{i}: {playlists[-1]}")
        i+=1

    def buildPlaylistsNextPageRequest():
        if mode == "fake":
            if getFakeResponse(iResponse+1):
                return "fakeRequest"
            return None
        return youtube.playlists().list_next(previous_request=request, previous_response=response)

    while request := buildPlaylistsNextPageRequest():
        response = executeRequest(request, iResponse := iResponse + 1)
        
        for playlist in response["items"]:
            title = playlist['snippet']['title']
            url = f"https://www.youtube.com/playlist?list={playlist['id']}"
            playlists.append(f"{title}\n{url}")
            print(f"{i}: {playlists[-1]}")
            i+=1

    playlists.sort(key=str.lower)


def set_list(playlists):
    text_list.config(state=tk.NORMAL)
    text_list.delete("1.0",tk.END)
    for pl in playlists:
        text_list.insert(tk.END,f"{pl}\n\n")
    text_list.config(state=tk.DISABLED)


def search():
    query = entry_search.get()
    if not query or len(query:=query.strip().lower()) == 0:
        set_list(playlists)
        return
    matches = [pl for pl in playlists if query in pl.lower()]
    set_list(matches)



scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
client_secrets_file = 'client_secret.json'
playlists = []
mode = "fake"


fontSize = 25
font = ("Arial",fontSize)

window = tk.Tk()
window.title("youtube")

entry_search = tk.Entry(master=window, width=30, font=font)
entry_search.pack()

btn_search = tk.Button(master=window, text="Search", command=search, font=font, width=8, height=2)
btn_search.pack()

text_list = tk.Text(master=window, state=tk.DISABLED, font=font, width=30, height=30)
text_list.pack()


initialize()
set_list(playlists)


window.mainloop()

