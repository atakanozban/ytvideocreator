import os
from moviepy.editor import AudioFileClip, ImageClip

def find_files(directory):
    mp3_files = []
    global image_file

    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            mp3_files.append(os.path.join(directory, filename))
        elif filename.endswith(".jpg") or filename.endswith(".png"):
            image_file = os.path.join(directory, filename)
    
    return mp3_files

def create_video(mp3_file, image_file):
    # Create audio clip
    audio_clip = AudioFileClip(mp3_file)
    
    # Create image clip and set duration to match audio
    image_clip = ImageClip(image_file)
    image_clip = image_clip.set_duration(audio_clip.duration)

    # Combine image and audio into a video
    video = image_clip.set_audio(audio_clip)
    
    # Extract the name of the mp3 file without extension for the video name
    output_file = os.path.splitext(os.path.basename(mp3_file))[0] + ".mp4"
    
    # Export video
    video.write_videofile(output_file, codec="libx264", fps=24)

if __name__ == "__main__":
    directory = "."
    
    mp3_files = find_files(directory)
    
    if mp3_files and image_file:
        for mp3_file in mp3_files:
            create_video(mp3_file, image_file)
            print(f"Video başarıyla {mp3_file} dosyasından oluşturuldu!")
    else:
        print("MP3 dosyası veya resim dosyası bulunamadı!")
