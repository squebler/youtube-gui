# My Custom YouTube GUI
Working on initial exploratory stuff; creating my own custom YouTube GUI, and training on python at the same time.

## search-playlists.py
search-playlists.py is a GUI that lets you search your playlists and jump to them quickly. I wanted this because I have a lot of playlists, and I sometimes find videos that I want to save to a specific playlist, but it's hard to find them in the web UI. And this has also resulted in me creating duplicate playlists.

Set `mode = "fake"` if you want to test without any web requests.

The app only gets the playlists at startup. So if you add/remove/rename your playlists, you'll have to restart to reflect that.


# Getting Started with YouTube / Google / OAuth APIs

Here's basically what I did for search-playlists.py:
1. Setup project on the Google Cloud Console
   1. Configure project scopes - which APIs you want access to. Basically permissions
   2. Setup OAuth 2.0 credentials for your project, and download client_secret.json file
2. Implement app using Python Client Library
   1. You only have to call like 2 functions, and it handles all the back-and-forth, under the covers.
   ```
   flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes=scopes)
   credentials = flow.run_local_server(open_browser=True)
   ```

## Links
Google OAuth 2.0 Overview  
https://developers.google.com/identity/protocols/oauth2 

Google OAuth 2.0 for Mobile & Desktop Apps  
https://developers.google.com/identity/protocols/oauth2/native-app 

YouTube API > Python Quick Start  
https://developers.google.com/youtube/v3/quickstart/python 

Google APIs > Python Client > YouTube API Reference  
https://googleapis.github.io/google-api-python-client/docs/dyn/youtube_v3.html 

Google APIs > Python Client Library > Core Reference  
https://googleapis.github.io/google-api-python-client/docs/epy/index.html 


The Python Client YouTube API Reference doesn't wrap the docs in the browser. One way you can make it wrap is right click on the text > Inspect. That should take you to the `<pre>` element in the Chrome dev console. Then in the Styles tab, you add `white-space: pre-wrap`. This seemed to affect all the docs for me. But if not you could add it to the `<head>` element styles, eg:
```
pre {
    white-space: pre-wrap;
}
```

