import py7zr
import os

def compress_other(other_files, output_folder, update_progress):
    # Locate the other files folder in the temporary directory
    temp_other_folder = os.path.join(output_folder, 'temp', 'other')

    # Ensure the folder exists
    if not os.path.exists(temp_other_folder):
        update_progress("Other files folder not found. Skipping compression.", 100)
        return

    # Define the output archive path
    archive_path = os.path.join(output_folder, 'other.7z')

    # Gather all files and calculate total size
    total_size = 0
    other_files = []

    for root, dirs, files in os.walk(temp_other_folder):
        for file in files:
            file_path = os.path.join(root, file)
            other_files.append(file_path)
            total_size += os.path.getsize(file_path)

    if not other_files:
        update_progress("No other files found for compression.", 100)
        return

    # Compress using ultra compression settings
    compressed_size = 0
    with py7zr.SevenZipFile(archive_path, 'w', filters=[
        {
            'id': py7zr.FILTER_LZMA2,
            'preset': 9
        }
    ]) as archive:
        for i, file_path in enumerate(other_files):
            archive.write(file_path, os.path.relpath(file_path, temp_other_folder))
            compressed_size += os.path.getsize(file_path)
            progress = (compressed_size / total_size) * 100
            update_progress(f"Compressed {compressed_size / (1024 * 1024):.2f} MB out of {total_size / (1024 * 1024):.2f} MB", progress)
