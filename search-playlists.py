from functools import partial
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import os
from requests import HTTPError
import tkinter as tk
import webbrowser


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

    def extractPlaylistDataFromResponse():
        nonlocal iPlaylist
        for playlist in response["items"]:
            title = playlist['snippet']['title']
            url = f"https://www.youtube.com/playlist?list={playlist['id']}"
            playlists.append({"title":title, "url":url})
            print(f"{iPlaylist}: {playlists[-1]}")
            iPlaylist+=1

    iPlaylist = 1
    extractPlaylistDataFromResponse()

    def buildPlaylistsNextPageRequest():
        if mode == "fake":
            if getFakeResponse(iResponse+1):
                return "fakeRequest"
            return None
        return youtube.playlists().list_next(previous_request=request, previous_response=response)

    while request := buildPlaylistsNextPageRequest():
        response = executeRequest(request, iResponse := iResponse + 1)
        extractPlaylistDataFromResponse()

    playlists.sort(key=lambda pl: pl["title"].lower())


def set_list(playlists):
    for widget in frame_playlist.winfo_children():
        widget.destroy()
    
    rowOn = 0
    for pl in playlists:
        btn_plCopyUrl = tk.Button(master=frame_playlist, font=fontRowButton, text="Copy URL", command=partial(copyUrlToClipboard, pl["url"]))
        btn_plCopyUrl.grid(row=rowOn, column=0, pady=10, padx=(10,0))

        btn_plOpenUrl = tk.Button(master=frame_playlist, font=fontRowButton, text="Open", command=partial(openUrl, pl["url"]))
        btn_plOpenUrl.grid(row=rowOn, column=1, pady=10, padx=(5,0))

        entry_plTitle = tk.Entry(master=frame_playlist, font=font, width=30, borderwidth=0)
        entry_plTitle.grid(row=rowOn, column=2, pady=10, padx=(10,10))
        entry_plTitle.insert(tk.END, pl["title"])

        rowOn += 1

    # update_idletasks causes the drawing of the widgets we just added
    frame_playlist.update_idletasks()
    # bbox computes the bounding box of all objects currently drawn on the canvas
    canvas_scrollArea.config(scrollregion=canvas_scrollArea.bbox("all"))


def search():
    query = entry_search.get()
    if not query or len(query:=query.strip().lower()) == 0:
        set_list(playlists)
        return
    matches = [pl for pl in playlists if query in pl["title"].lower()]
    set_list(matches)


def copyUrlToClipboard(url):
    print(f"url: {url}")
    window.clipboard_clear()
    window.clipboard_append(url)
    window.update()


def openUrl(url):
    print(f"url: {url}")
    webbrowser.open_new_tab(url)


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
client_secrets_file = 'client_secret.json'
playlists = []
mode = "fake"


fontSize = 25
font = ("Arial",fontSize)
fontSizeRowButton = 15
fontRowButton = ("Arial",fontSizeRowButton)

window = tk.Tk()
window.title("youtube")
window.geometry("765x900")

entry_search = tk.Entry(master=window, width=30, font=font)
entry_search.pack(anchor="nw", padx=10, pady=(10,0))

btn_search = tk.Button(master=window, text="Search", command=search, font=fontRowButton)
btn_search.pack(anchor="w", padx=10, pady=5)

window.bind('<Return>', lambda event=None: btn_search.invoke())

# I guess the following is how you're supposed to setup a scrollbar for a frame.
# Not sure because I got it from ChatGPT. It works, but might be a simpler way?

canvas_scrollArea = tk.Canvas(master=window)
scrollbar = tk.Scrollbar(master=window, orient="vertical", command=canvas_scrollArea.yview)
canvas_scrollArea.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y", pady=(10,0))
canvas_scrollArea.pack(side="left", fill="both", expand=True, pady=(10,0))

frame_playlist = tk.Frame(master=canvas_scrollArea, bg="white")
canvas_scrollArea.create_window((0,0), window=frame_playlist, anchor="nw")


initialize()
set_list(playlists)


window.mainloop()

