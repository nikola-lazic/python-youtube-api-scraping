# **Python YouTube API Scraping**
This is a set of Python functions for scraping data from YouTube, including channel data and video data. 
</br>It's necessary to have YouTube Data API V3 and it's free!
</br>These functions were written by watching YouTube tutorial by [Thu Vu](https://github.com/thu-vu92). Here is YouTube tutorial: [Youtube API for Python: How to Create a Unique Data Portfolio Project](https://www.youtube.com/watch?v=D56_Cx36oGY&ab_channel=ThuVudataanalytics)

## **Credentials**
YouTube Data API V3 are free and you could get them on Google Developers page.
In this project, they are stored in credentials.py:
```
yt_api_key = ""
yt_api_service_name = "youtube"
yt_api_version = "v3"
```


## **List of Functions**
For using these function, we first need to create an YouTube API client:
```
yt_client = build(
    credentials.yt_api_service_name,
    credentials.yt_api_version,
    developerKey=credentials.yt_api_key,
)
```
 - Get YT channel ID
 - Get Channel data
 - Get Videos IDs from Playlist
 - Get Video data
 - Get YT Comments from Video
 - Get Video ID

## **Requirements**
```
pip install -r requirements.txt
```

## **References**
- GitHub [Thu Vu](https://github.com/thu-vu92)
- [Youtube API for Python: How to Create a Unique Data Portfolio Project](https://www.youtube.com/watch?v=D56_Cx36oGY&ab_channel=ThuVudataanalytics)
- [Youtube API Data Reference](https://developers.google.com/youtube/v3/docs)
- [YouTube Data API - Google Developers](https://console.cloud.google.com/apis/)