import ffmpeg
import os

#please note on windows you have to put ffmpeg both to path and next to python.exe wherever it is installed. hooray

#istg this almost made me insane

def compress_videos(video_files, output_folder, update_progress):
    # Locate the videos folder in the temporary garbage
    temp_videos_folder = os.path.join(output_folder, 'temp', 'videos')

    # Ensure the folder exists
    if not os.path.exists(temp_videos_folder):
        update_progress("Videos folder not found. Skipping compression.", 100)
        return

    # Gather all video files
    video_files = []
    for root, dirs, files in os.walk(temp_videos_folder):
        for file in files:
            video_files.append(os.path.join(root, file))

    if not video_files:
        update_progress("No video files found for compression.", 100)
        return

    # Create the output videos folder
    output_videos_folder = os.path.join(output_folder, 'videos')
    os.makedirs(output_videos_folder, exist_ok=True)

    # Compress each video
    for i, video_file in enumerate(video_files):
        try:
            # Ensure the file exists
            if not os.path.isfile(video_file):
                update_progress(f"File not found: {video_file}", 100)
                continue

            # Define the output file path
            base_name = os.path.basename(video_file).split('.')[0]
            output_file = os.path.join(output_videos_folder, f"{base_name}.mp4")

            # Normalize paths
            video_file = os.path.normpath(video_file)
            output_file = os.path.normpath(output_file)

            # Define ffmpeg options
            options = {
                'b:v': '500k',
                'crf': 28,
                'preset': 'slow',
                'movflags': '+faststart',
                'vf': 'scale=iw:-1',
                'map_metadata': '0'
            }

            # Use FFmpeg to compress the video with high compression settings
            (
                ffmpeg
                .input(video_file)
                .output(output_file, vcodec='libx264', **options)
                .global_args('-hide_banner', '-loglevel', 'error')
                .run()
            )

            update_progress(f"Compressed {os.path.basename(video_file)}", (i + 1) / len(video_files) * 100)
        except Exception as e:
            update_progress(f"Error compressing {video_file}: {str(e)}")