from flask import Flask, request, Response
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

@app.route('/subtitles', methods=['POST'])
def get_subtitles():
    youtube_url = request.form.get('url')
    if not youtube_url:
        return "No URL provided!", 400

    # Extract video ID from URL (handles youtu.be and youtube.com)
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return "Invalid YouTube URL!", 400

    try:
        # Fetch subtitles (prefer English)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        srt_content = transcript_to_srt(transcript)
        return Response(srt_content, mimetype='text/plain', headers={
            'Content-Disposition': 'attachment; filename="subtitles.srt"'
        })
    except Exception as e:
        return f"Error: {str(e)}", 500

def extract_video_id(url):
    # Match youtube.com or youtu.be URLs
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
        r'(?:https?:\/\/)?youtu\.be\/([^?]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def transcript_to_srt(transcript):
    srt = ''
    for i, entry in enumerate(transcript, 1):
        start = entry['start']
        duration = entry['duration']
        end = start + duration
        start_time = format_time(start)
        end_time = format_time(end)
        text = entry['text'].replace('\n', ' ')
        srt += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

if __name__ == "__main__":
    app.run(debug=True)