#!/usr/bin/env python3
"""Creates The Algorithm Evolution Atlas's watch-in-order playlists in your own YouTube account.

Run it once a day until it says it is finished. Google's free daily limit (10,000 units; each video added costs 50)
allows about 190 videos a day, so the 25 playlists take about 5 days. The script remembers where it stopped, in
atlas_progress.json beside it, and also checks what each playlist already holds, so running it twice never adds a
video twice.

Setup (once): see the steps in README-youtube-playlists.md, or in short:
  1. pip3 install google-api-python-client google-auth-oauthlib
  2. Put the OAuth file you downloaded from Google Cloud next to this script, named client_secret.json
  3. python3 make_youtube_playlists.py            (a browser window opens once to sign in)

Options:
  --dry-run            show what would be created, without signing in or changing anything
  --privacy unlisted   make the new playlists unlisted (default: private); "public" also works
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLIENT = HERE / "client_secret.json"
TOKEN = HERE / "atlas_token.json"
PROGRESS = HERE / "atlas_progress.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# The 25 playlists, in book order: [number, title, topics covered, [video IDs in order]]
PLAYLISTS = __DATA__


def load_progress():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text())
    return {"playlists": {}, "skipped": {}}


def save_progress(p):
    PROGRESS.write_text(json.dumps(p, indent=1))


def connect():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Missing libraries. Run:  pip3 install google-api-python-client google-auth-oauthlib")
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None  # an app in Google's "testing" mode gets sign-ins that last 7 days; sign in again
    if not creds or not creds.valid:
        if not CLIENT.exists():
            sys.exit(f"Not found: {CLIENT}\nDownload your OAuth client (Desktop app) from Google Cloud and save it there as client_secret.json.")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def reason(err):
    try:
        return json.loads(err.content.decode())["error"]["errors"][0]["reason"]
    except Exception:
        return ""


class QuotaDone(Exception):
    pass


def call(request):
    from googleapiclient.errors import HttpError
    for attempt in range(5):
        try:
            return request.execute()
        except HttpError as e:
            r = reason(e)
            if r in ("quotaExceeded", "dailyLimitExceeded"):
                raise QuotaDone()
            if r == "rateLimitExceeded" or e.resp.status in (500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("YouTube kept refusing; try again later.")


def my_playlists(yt):
    """Title -> id for the playlists already in the account, so a lost progress file never causes duplicates."""
    out, token = {}, None
    while True:
        r = call(yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=token))
        for it in r.get("items", []):
            out.setdefault(it["snippet"]["title"], it["id"])
        token = r.get("nextPageToken")
        if not token:
            return out


def items_in(yt, pid):
    ids, token = set(), None
    while True:
        r = call(yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50, pageToken=token))
        for it in r.get("items", []):
            ids.add(it["contentDetails"]["videoId"])
        token = r.get("nextPageToken")
        if not token:
            return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    args = ap.parse_args()

    total = sum(len(p[3]) for p in PLAYLISTS)
    if args.dry_run:
        for num, title, span, ids in PLAYLISTS:
            print(f"{num:2d}. {title}  ({len(ids)} videos: {span})")
        print(f"\n{len(PLAYLISTS)} playlists, {total} videos. About {-(-total // 190)} days at Google's free daily limit.")
        return

    from googleapiclient.errors import HttpError
    yt = connect()
    prog = load_progress()
    added_today = 0
    try:
        existing = my_playlists(yt)
        for num, title, span, ids in PLAYLISTS:
            key = str(num)
            pid = prog["playlists"].get(key) or existing.get(title)
            if not pid:
                body = {"snippet": {"title": title,
                                    "description": f"The Algorithm Evolution Atlas, watched in book order: {span}. {len(ids)} videos."},
                        "status": {"privacyStatus": args.privacy}}
                pid = call(yt.playlists().insert(part="snippet,status", body=body))["id"]
                print(f"Created playlist {num}: {title}")
            prog["playlists"][key] = pid
            save_progress(prog)
            have = items_in(yt, pid)
            skipped = set(prog["skipped"].get(key, []))
            todo = [v for v in ids if v not in have and v not in skipped]
            if not todo:
                print(f"{num:2d}. {title}: complete ({len(have)} videos)")
                continue
            print(f"{num:2d}. {title}: adding {len(todo)} of {len(ids)}")
            for v in todo:
                body = {"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": v}}}
                try:
                    call(yt.playlistItems().insert(part="snippet", body=body))
                    added_today += 1
                except HttpError as e:
                    if reason(e) in ("videoNotFound", "forbidden", "playlistItemsNotAccessible") or e.resp.status == 404:
                        prog["skipped"].setdefault(key, []).append(v)  # removed or private since the list was made
                        save_progress(prog)
                        print(f"    skipped {v} (no longer available)")
                        continue
                    raise
                time.sleep(0.2)
        nskip = sum(len(v) for v in prog["skipped"].values())
        print(f"\nFinished: all {len(PLAYLISTS)} playlists are complete" + (f" ({nskip} videos were no longer available)." if nskip else "."))
    except QuotaDone:
        print(f"\nAdded {added_today} videos today. Google's daily limit is reached; it resets at midnight Pacific time.")
        print("Run the same command again tomorrow; it carries on where it stopped.")
    finally:
        save_progress(prog)


if __name__ == "__main__":
    main()
