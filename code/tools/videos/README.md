# The video list: how it is made

The list is [`book/videos/`](../../../book/videos/README.md): for every topic of the book (Chapter 1, Eras 1 to 8 and the principles catalog), its concepts from the simplest to the most advanced, each with videos that explain it. The concepts are listed in [`concepts.py`](concepts.py), 380 of them; the results are kept in `book/videos/videos.json`, and [`videos.py`](videos.py) builds the interactive page (`index.html`) and the GitHub page (`README.md`) from them.

## One round

A round handles one concept, then waits 40 seconds, so that the video site is not asked too often.

1. `python3 code/tools/videos/videos.py next` prints the next concept that has not been searched, or whose last round failed.
2. Search the web for it, limited to `youtube.com`. When the concept is advanced and YouTube has nothing suitable, a second search may look for lecture videos on course and conference sites.
3. Choose up to three candidates, simplest first: accurate, clear, from a named teacher, course, museum, university or the inventors themselves. Leave out clickbait, claims the book's sources contradict, Shorts, reuploads of someone else's lecture, and videos that only mention the concept in passing.
4. Confirm each one. A YouTube watch page cannot be opened from the build environment, so the check is YouTube's own oEmbed lookup (`https://www.youtube.com/oembed?url=<watch URL>&format=json`), which returns the video's real title and channel; a video that it does not confirm is not listed. A video on another site is listed only if its page opens.
5. Give each video a level: **Start** (no background needed), **Deeper** (university level), **Scholar** (research talks, and the inventors themselves).
6. Write the round to a JSON file (the format is at the top of `videos.py`) and run `python3 code/tools/videos/videos.py record FILE`. It merges the round and rebuilds both pages. A round whose search or checks failed is recorded with an `error` and is tried again later.
7. Wait 40 seconds before the next search.

After every round the branch is committed and pushed; every ten rounds the published page is updated.

## Rules carried over from the book

- Every listed video was checked on the date shown in `videos.json` (`checked`).
- Titles and channels are copied from the check, not retyped from memory.
- Nothing is filled in: a concept with no suitable video says so.
