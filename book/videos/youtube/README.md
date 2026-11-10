# Make the playlists in your own YouTube account

`make_youtube_playlists.py` creates the 25 watch-in-order playlists from [playlists.md](../playlists.md) in your YouTube account, through YouTube's official API. Nothing passes through any other service.

Google's free daily limit allows about 190 videos a day, so the 912 videos take about **5 days**: run the same command once a day until it says *Finished*. It remembers where it stopped (`atlas_progress.json`), and checks what each playlist already holds, so running it twice never adds a video twice.

## One-time setup (about 15 minutes)

You need Python 3 and the YouTube account you want the playlists in.

1. **Create a project.** Open <https://console.cloud.google.com/>, sign in with the Google account that owns your YouTube channel, and create a new project (any name, for example *Atlas playlists*).
2. **Turn on the YouTube API.** In that project: *APIs & Services → Library*, search for **YouTube Data API v3**, open it and click **Enable**.
3. **Set up the sign-in screen.** Go to *APIs & Services → OAuth consent screen* (on newer consoles it is called *Google Auth Platform*). Click *Get started* and fill in:
   - App name: anything, for example *Atlas playlists*; support email: yours.
   - Audience: **External**.
   - Contact email: yours. Accept the terms and create.
   - Then under **Audience → Test users**, click *Add users* and add your own Gmail address. (The app stays in "testing"; only you can use it.)
4. **Create the sign-in file.** Under *Clients* (or *Credentials → Create credentials → OAuth client ID*), choose application type **Desktop app**, give it any name, and create it. Click **Download JSON**.
5. **Put the files together.** Make a folder, put `make_youtube_playlists.py` in it, and save the downloaded file in the same folder, renamed to **`client_secret.json`**.
6. **Install the two libraries** (in Terminal):

   ```
   pip3 install google-api-python-client google-auth-oauthlib
   ```

## Every day

In Terminal, in that folder:

```
python3 make_youtube_playlists.py
```

- The first time, a browser window opens. Choose your account (pick the right channel if you have more than one). Google warns that it *hasn't verified this app*: click **Continue**, since it is your own app, then allow access.
- It creates the playlists (private), adds videos in book order, and stops when the daily limit is reached, printing *Run the same command again tomorrow*. The limit resets at midnight Pacific time.
- When everything is in, it prints *Finished*. Videos that were removed from YouTube since the list was made are skipped and counted.

Options: `--dry-run` lists the 25 playlists without signing in; `--privacy unlisted` (or `public`) for new playlists instead of private.

If, after a week, it says the sign-in expired (apps in testing mode get sign-ins that last 7 days), delete `atlas_token.json` and run it again; it signs in afresh and carries on.

Keep `client_secret.json` and `atlas_token.json` private: they give access to your YouTube account.
