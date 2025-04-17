import os
import moviepy.editor as mp
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from PIL import Image

def create_video_from_media(image_path, audio_path, output_path):
    try:
        audio_clip = mp.AudioFileClip(audio_path)
        
        video_width, video_height = 1920, 1080
        
        image_clip = mp.ImageClip(image_path)
        img_width, img_height = image_clip.size
        
        x_center = (video_width - img_width) / 2
        y_center = (video_height - img_height) / 2
        
        background = mp.ColorClip(size=(video_width, video_height), color=(0, 0, 0)).set_duration(audio_clip.duration)
        image_clip = image_clip.set_position((x_center, y_center)).set_duration(audio_clip.duration)
        
        final_clip = mp.CompositeVideoClip([background, image_clip]).set_audio(audio_clip)
        
        # Video create and save settings
        final_clip.write_videofile(output_path, codec='libx264', fps=24, audio_codec='aac')
        print(f"Video created: {output_path}")
    except Exception as e:
        print(f"An error occured while creating the video: {e}")
        return False
    return True

def get_authenticated_service():
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None

    if os.path.exists('token.json'):
        try:
            creds, _ = google.auth.load_credentials_from_file('token.json')
        except Exception as e:
            print("Token file is invaild or unavailable, reauthorization is in progress...")
            os.remove('token.json')
            creds = None

    # If token is unavailable or invaild, start OAuth feed (offline access and by adding consent)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build("youtube", "v3", credentials=creds)

def upload_video_to_youtube(youtube, video_file, title, category='10', privacy_status='private'):
    try:
        request_body = {
            'snippet': {
                'title': title,
                'categoryId': category
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/mp4')
        request = youtube.videos().insert(
            part=','.join(request_body.keys()),
            body=request_body,
            media_body=media
        )
        response = request.execute()
        print(f"Video successfully uploaded! Video ID: {response['id']}")
    except Exception as e:
        print(f"An error occured while uploading the video: {e}")
        return False
    return True

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get image files (for example: .jpg, .jpeg, .png)
    image_extensions = ('.jpg', '.jpeg', '.png')
    image_files = [f for f in os.listdir(base_dir) if f.lower().endswith(image_extensions)]
    if not image_files:
        print("Error: No image file found!")
        return
    # We are going to use first image file which is we found on the same directory.
    image_file = os.path.join(base_dir, image_files[0])
    print(f"Found image: {image_file}")

    # We are going to use all of audio files which is we found on the same directory.
    mp3_files = [f for f in os.listdir(base_dir) if f.lower().endswith('.mp3')]
    if not mp3_files:
        print("Error: No MP3 file not found!")
        return

    output_folder = os.path.join(base_dir, "videos")
    os.makedirs(output_folder, exist_ok=True)
    
    # Run OAuth authorization feed once and create the YouTube service.
    youtube_service = get_authenticated_service()
    
    for mp3 in mp3_files:
        mp3_path = os.path.join(base_dir, mp3)
        video_filename = f"{os.path.splitext(mp3)[0]}.mp4"
        video_path = os.path.join(output_folder, video_filename)
        
        if create_video_from_media(image_file, mp3_path, video_path):
            title = os.path.splitext(mp3)[0]
            if upload_video_to_youtube(youtube_service, video_path, title):
                print(f"{video_filename} successfully uploaded, deleting file in progress...")
                try:
                    os.remove(video_path)
                    print(f"{video_filename} is deleted.")
                except Exception as e:
                    print(f"An error occured while deleting the {video_filename}: {e}")
            else:
                print(f"{video_filename} can't uploaded to YouTube. File is saving.")

if __name__ == "__main__":
    main()
