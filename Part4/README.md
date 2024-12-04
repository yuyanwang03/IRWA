# Part 4: Search Engine with Analytics

This is the implementation of a search engine with analytics for IRWA (Information Retrieval and Web Analytics). It includes session tracking, user analytics, and an interactive dashboard.

[!NOTE]
You must have the JSON file with the original tweets info located in the folder: `static/farmers-protest-tweets.json`
The program will throw an error if the file is missing!

## How to run it

After following the instructions steps 0, 1, and 3 in the root README.md do:

```
python web_app.py
```

You could then open the application in your browser at: http://127.0.0.1:8088

## 4. Features

•	Search Engine: Enter a query on the homepage to retrieve relevant results.

•	Session Analytics: Tracks user sessions, queries, clicks, and durations.

•	General Analytics: View usage statistics on /analytics.

•	All Sessions Analytics: Aggregates and displays data across all sessions on /all_sessions.

## Demo Video

Below is a 30-second demo showcasing the search engine and analytics functionality:

<video width="640" height="360" controls>
  <source src="./static/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>


<img src="https://github.com/yuyanwang03/IRWA/blob/main/Part4/static/demo.gif" width="640" height="400"/>