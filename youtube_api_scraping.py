# Importing modules:
from googleapiclient.discovery import build
import re

# Importing credentials
import credentials


# INPUT DATA:
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=KwkvWugKER4"


# Create an YouTube API client and get credentials:
yt_client = build(
    credentials.yt_api_service_name,
    credentials.yt_api_version,
    developerKey=credentials.yt_api_key,
)


def get_channel_id(yt_client, video_id):
    """Get the channel ID of a video.
    Params:

    youtube: the build object from googleapiclient.discovery
    video_id: the video ID

    Returns:
    Channel ID of the video.
    """

    request = yt_client.videos().list(part="snippet", id=video_id)
    response = request.execute()

    channel_id = response["items"][0]["snippet"]["channelId"]

    print(channel_id)
    return channel_id


def get_channel_data(yt_client, channel_ids):
    """
    Get channel stats: channelName, no. of subscribers, no of views,
    totalVideos.

    Params:
    ------
    youtube: build object of Youtube API
    channel_ids: list of channel IDs

    Returns:
    ------
    dataframe with all channel stats for each channel ID

    """

    all_data = []

    request = yt_client.channels().list(
        part="snippet,contentDetails,statistics", id=",".join(channel_ids)
    )
    response = request.execute()

    # loop through items
    for item in response["items"]:
        data = {
            "channelName": item["snippet"]["title"],
            "subscribers": item["statistics"]["subscriberCount"],
            "views": item["statistics"]["viewCount"],
            "totalVideos": item["statistics"]["videoCount"],
            # "playlistId": item["contentDetails"]["relatedPlaylists"]["uploads"],
        }

        all_data.append(data)
    print(all_data)
    return all_data


def get_videos_ids_from_playlist(yt_client, playlist_id):
    """This function takes in a youtube object
    and a playlist_id string as arguments. It makes a request to the YouTube API to
    get all the video IDs in a given playlist, even if there are more than 50 videos
    in the playlist (which is the maximum number of results returned in a single API request).
    It does this by making multiple requests, each for a different page of results, until
    it has retrieved all of the video IDs. The video IDs are then returned as a list.

    Args:
        youtube (object): instance of the googleapiclient.discovery.Resource class
        playlist_id (string): This is ID of an youtube playlist

    Returns:
        list: The video IDs are then returned as a list.
    """
    # Create an empty list to store video IDs
    video_ids = []

    # Make a request to the YouTube API to get the first page of playlist items
    request = yt_client.playlistItems().list(
        part="snippet,contentDetails", playlistId=playlist_id, maxResults=50
    )
    # Execute the request and get the response
    response = request.execute()

    # Loop through each item in the response and append the video ID to the list
    for item in response["items"]:
        video_ids.append(item["contentDetails"]["videoId"])

    # Check if there are more pages of results
    next_page_token = response.get("nextPageToken")
    while next_page_token is not None:
        # Make a request to the YouTube API for the next page of results
        request = yt_client.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        # Execute the request and get the response
        response = request.execute()

        # Loop through each item in the response and append the video ID to the list
        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        # Check if there are more pages of results
        next_page_token = response.get("nextPageToken")

    # Return the list of video IDs
    return video_ids


def get_video_data(yt_client, video_ids):
    """This function takes in a youtube object and a list of video IDs.
    It makes a request to the YouTube API to get detailed information
    about each video, including its title, description, view count, like count, and more.
    It then extracts the desired information from the response and stores it
    in a list of dictionaries, with each dictionary representing the
    information for one video. Finally, it converts the list of dictionaries
    to a pandas DataFrame and returns it.

    Args:
        youtube (object): instance of the googleapiclient.discovery.Resource class
        video_ids (string): list of video IDs

    Returns:
        Pandas DataFrame: list of dictionaries are converted into to a pandas DataFrame
    """

    # Create an empty list to store the video information
    all_video_info = []

    # Loop through the video IDs, 50 at a time, to make requests to the YouTube API
    for i in range(0, len(video_ids), 50):
        # Make a request to the YouTube API to get information about the videos
        request = yt_client.videos().list(
            part="snippet,contentDetails,statistics", id=",".join(video_ids[i : i + 50])
        )
        # Execute the request and get the response
        response = request.execute()

        # Loop through each video in the response and extract the desired information
        for video in response["items"]:
            # Define a dictionary of the information we want to keep for each video
            stats_to_keep = {
                "snippet": [
                    "channelTitle",
                    "title",
                    "description",
                    "tags",
                    "publishedAt",
                ],
                "statistics": [
                    "viewCount",
                    "likeCount",
                    "commentCount",
                ],
                "contentDetails": ["duration"],
            }

            # Create a dictionary to store the information for this video
            video_info = {}
            video_info["video_id"] = video["id"]

            # Loop through the different types of information we want to keep
            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    # Try to get the value of this piece of information from the video's data
                    try:
                        video_info[v] = video[k][v]
                    # If the piece of information is not present, set the value to None
                    except:
                        video_info[v] = None

            # Append the video's information to the list of all video information
            all_video_info.append(video_info)

    # Convert the list of video information dictionaries to a pandas DataFrame and return it
    return all_video_info


def get_yt_comments_from_video(yt_client, video_ids):
    for video_id in video_ids:  # loop through each video ID
        try:
            comments_in_video = (
                []
            )  # create an empty list to hold all the comments for the current video
            next_page_token = None  # set initial value for the next page token to None
            count = 0  # set initial value for the count of comments retrieved to 0

            while (
                count < 1000
            ):  # continue while less than 1000 comments have been retrieved
                request = yt_client.commentThreads().list(
                    part="snippet,replies", videoId=video_id, pageToken=next_page_token
                )  # create a request to get the comment threads for the current video
                response = request.execute()  # execute the request

                for comment in response[
                    "items"
                ]:  # loop through each comment in the response
                    comments_in_video.append(  # add the comment's text and number of likes to the list of comments for the current video
                        {
                            "text": comment["snippet"]["topLevelComment"]["snippet"][
                                "textOriginal"
                            ],
                            "likes": comment["snippet"]["topLevelComment"]["snippet"][
                                "likeCount"
                            ],
                        }
                    )
                next_page_token = response.get(
                    "nextPageToken", None
                )  # get the next page token, if any
                if (
                    next_page_token is None
                ):  # if there are no more pages, break out of the loop
                    break
                count += 100  # increment the count of comments retrieved by 100

            print(comments_in_video)
            return comments_in_video

        except:
            # When error occurs - most likely because comments are disabled on a video
            print(
                f"Could not get comments for video ID={video_id}. Comments are probably disabled on this video."
            )


def get_video_id(video_url):
    # Get video_id by providing YouTube link
    video_id = re.search(r"v=([\w-]+)", video_url).group(1)
    print(video_id)
    return video_id


if __name__ == "__main__":
    video_id = get_video_id(YOUTUBE_VIDEO_URL)

    # YouTube comments:
    get_yt_comments_from_video(yt_client, [video_id])

    # Get channel ID:
    channel_id = get_channel_id(yt_client, video_id)

    # Channel data:
    get_channel_data(yt_client, [channel_id])
