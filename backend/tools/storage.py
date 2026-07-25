import os

MAX_STORAGE = 2 * 1024 * 1024 * 1024

def get_folder_size(folder):

    total_size = 0

    for dirpath, dirnames, filenames in os.walk(folder):

        for filename in filenames:

            file_path = os.path.join(
                dirpath,
                filename
            )

            total_size += os.path.getsize(file_path)

    return total_size
