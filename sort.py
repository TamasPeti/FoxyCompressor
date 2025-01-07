import os
import shutil

def sort_files(input_folder, output_folder):
    categories = {
        'documents': ['.txt', '.text', '.rtf', '.doc', '.docx', '.docm', '.dot', '.dotx', '.pdf', '.odt', '.xls', '.xlsx', '.xlsm', '.xlt', '.xltx', '.csv', '.ods', '.ppt', '.pptx', '.pptm', '.pot', '.potx', '.odp', '.html', '.htm', '.css', '.js', '.py'],
        'audio': ['.mp3', '.wav', '.aac', '.wma', '.mid', '.midi'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.svg'],
        'videos': ['.mp4', '.avi', '.mpeg', '.mpg', '.wmv', '.mov', '.flv'],
        'other': ['.exe', '.app', '.zip', '.rar', '.tar', '.tar.gz', '.tgz', '.mdb', '.accdb', '.sql', '.reg', '.ini', '.dll']
    }

    sorted_files = {category: [] for category in categories.keys()}

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            for category, extensions in categories.items():
                if ext in extensions:
                    sorted_files[category].append(file_path)
                    break
            else:
                sorted_files['other'].append(file_path)

    # Move files to their respective folders
    for category, files in sorted_files.items():
        category_folder = os.path.join(output_folder, 'temp', category)
        os.makedirs(category_folder, exist_ok=True)
        for file in files:
            shutil.move(file, os.path.join(category_folder, os.path.basename(file)))

    return sorted_files