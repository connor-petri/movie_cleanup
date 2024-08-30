import os
import shutil
import schedule
import time


def move_files_except_largest(dir: str) -> None:
    filenames: list[str] = [entry for entry in os.listdir(dir) if os.path.isfile(os.path.join(dir, entry))]

    largest_file = max(filenames, key=lambda f: os.path.getsize(os.path.join(dir, f)))
    filenames.remove(largest_file)  # remove the largest file from the list
                
    # Move all other files to 'extras'
    for filename in filenames:
        if not os.path.isdir(os.path.join(dir, "extras")):
            os.mkdir(os.path.join(dir, "extras"))

        shutil.move(os.path.join(dir, filename), os.path.join(dir, "extras"))


def scan_movies(dir: str) -> None:
    dirnames: list[str] = [entry for entry in os.listdir(dir) if os.path.isdir(os.path.join(dir, entry))]

    for dirname in dirnames:
        move_files_except_largest(os.path.join(dir, dirname))


if __name__ == "__main__":
    with open("movie-path.txt", "r") as f:
        root_dir = f.read().strip()
    
    schedule.every().day.at("00:00").do(scan_movies, root_dir)

    while True:
        schedule.run_pending()
        time.sleep(1)