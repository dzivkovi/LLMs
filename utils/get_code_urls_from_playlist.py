"""Script to generate markdown from a YouTube playlist."""

import re
import os
import argparse
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Use the environment variable
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

YOUTUBE = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

TRIGGER_WORDS = ['colab', 'code', 'cookbook', 'github', 'notebook']

def get_playlist_title_and_owner(playlist_id):
    """Get the playlist title and owner from the playlist id."""
    request = YOUTUBE.playlists().list(  # pylint: disable=no-member
        part="snippet",
        id=playlist_id
    )
    response = request.execute()

    if 'items' in response and response['items']:
        playlist_title = response['items'][0]['snippet']['title']
        channel_id = response['items'][0]['snippet']['channelId']
    else:
        print(f"No data returned for playlist: {playlist_id}")
        return "", ""

    request = YOUTUBE.channels().list(  # pylint: disable=no-member
        part="snippet",
        id=channel_id
    ) # pylint: disable=assignment-from-no-return
    response = request.execute()

    if 'items' in response and response['items']:
        channel_title = response['items'][0]['snippet']['title']
    else:
        print(f"No data returned for channel: {channel_id}")
        return playlist_title, ""

    return f"{channel_title} - {playlist_title}"

def get_video_ids_and_titles_from_playlist(playlist_id):
    """Get the video ids and titles from the playlist id."""
    request = YOUTUBE.playlistItems().list(  # pylint: disable=no-member
        part="snippet",
        maxResults=50,
        playlistId=playlist_id
    )
    response = request.execute()

    video_data = []
    for item in response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        video_title = item['snippet']['title']
        video_data.append((video_id, video_title))

    return video_data

def get_video_description(video_id):
    """Get the description of a video given its id."""
    request = YOUTUBE.videos().list(  # pylint: disable=no-member
        part="snippet",
        id=video_id
    )
    response = request.execute()

    if 'items' in response and response['items']:
        return response['items'][0]['snippet']['description']
    else:
        print(f"No data returned for video: {video_id}")
        return ""

def strip_non_alphanumeric(context):
    """Remove non-alphanumeric characters from the end of a string."""
    return re.sub(r'\W+$', '', context)

def get_urls_from_description(description):
    """Extract URLs and their surrounding context from a description."""
    url_regex = r'http[s]?://(?:[a-zA-Z]|[\d]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_regex, description)
    url_matches = re.finditer(url_regex, description)
    url_positions = [match.start() for match in url_matches]
    urls_and_context = []

    for i, url in enumerate(urls):
        start = url_positions[i] - 1
        while start > 0 and description[start] != '\n':
            start -= 1
        context = description[start:url_positions[i]].strip().rstrip(':')
        context = strip_non_alphanumeric(context)  # Strip non-alphanumeric characters from the end
        urls_and_context.append((url, context))

    return urls_and_context

def get_args():
    """Get command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Extract URLs from YouTube playlist video descriptions.')
    parser.add_argument('-p', '--playlist', help='YouTube Playlist ID', required=True)
    args = parser.parse_args()
    return args

def contains_trigger_word(context):
    """Check if a given context contains any trigger words."""
    context_words = context.lower().split()
    return any(word in context_words for word in TRIGGER_WORDS)

def generate_markdown_file(playlist_title, video_data):
    """Generate a markdown file from playlist data."""
    markdown_filename = os.path.join(os.getcwd(), playlist_title.replace(" ", "_") + ".md")

    with open(markdown_filename, 'w', encoding='utf-8') as markdown_file:
        markdown_file.write(f'# Playlist: {playlist_title}\n\n')

        for i, (video_id, video_title) in enumerate(video_data, start=1):
            print(f'\nLesson {i}: {video_title}')  # Print to stdout

            # Bold lesson line and two spaces for a new line in markdown
            markdown_file.write(f'\n**Lesson {i}: {video_title}**  \n')

            description = get_video_description(video_id)
            urls_and_context = get_urls_from_description(description)
            code_urls = [(url, context) for url, context in urls_and_context if contains_trigger_word(context)]  # pylint: disable=line-too-long

            if code_urls:
                for url, context in code_urls:
                    # Print to stdout
                    print(f'{context}: {url}')
                    # Two spaces for a new line in markdown
                    markdown_file.write(f'{context}: {url}  \n')
            else:
                print('No link to code found')
                markdown_file.write('No link to code found  \n')

            print(f'Video: https://www.youtube.com/watch?v={video_id}')
            markdown_file.write(f'Video: https://www.youtube.com/watch?v={video_id}  \n')

def main():
    """Main function of the script."""
    args = get_args()
    playlist_id = args.playlist

    playlist_title = get_playlist_title_and_owner(playlist_id)
    print(f'Playlist: {playlist_title}')  # Print to stdout

    video_data = get_video_ids_and_titles_from_playlist(playlist_id)

    generate_markdown_file(playlist_title, video_data)

if __name__ == "__main__":
    main()
