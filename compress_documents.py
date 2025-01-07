import py7zr
import os

def compress_documents(document_files, output_folder, update_progress):
    # Locate the documents folder in the temporary directory
    temp_documents_folder = os.path.join(output_folder, 'temp', 'documents')

    # Ensure the folder exists
    if not os.path.exists(temp_documents_folder):
        update_progress("Documents folder not found. Skipping compression.", 100)
        return

    # Define the output archive path
    archive_path = os.path.join(output_folder, 'documents.7z')

    # Gather all files and calculate total size
    total_size = 0
    document_files = []

    for root, dirs, files in os.walk(temp_documents_folder):
        for file in files:
            file_path = os.path.join(root, file)
            document_files.append(file_path)
            total_size += os.path.getsize(file_path)

    if not document_files:
        update_progress("No document files found for compression.", 100)
        return

    # Compress using ultra compression settings
    compressed_size = 0
    with py7zr.SevenZipFile(archive_path, 'w', filters=[
        {
            'id': py7zr.FILTER_LZMA2,
            'preset': 9
        }
    ]) as archive:
        for i, file_path in enumerate(document_files):
            archive.write(file_path, os.path.relpath(file_path, temp_documents_folder))
            compressed_size += os.path.getsize(file_path)
            progress = (compressed_size / total_size) * 100
            update_progress(f"Compressed {compressed_size / (1024 * 1024):.2f} MB out of {total_size / (1024 * 1024):.2f} MB", progress)
