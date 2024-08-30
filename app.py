import os
import shutil
import schedule
from time import sleep
from datetime import datetime
from flask import Flask

app = Flask(__name__)

def log(msg: str) -> None:
    with open(f"./logs/{datetime.now().strftime('%Y-%m-%d')}.txt", "a") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S.%f')[:12]}: {msg}\n")


def move_files_except_largest(dir: str) -> None:
    log(f"Scanning {dir}...")
    filenames: list[str] = [entry for entry in os.listdir(dir) if os.path.isfile(os.path.join(dir, entry))]

    if not filenames:
        log(f"No files found in {dir}")

    largest_file: str = max(filenames, key=lambda f: os.path.getsize(os.path.join(dir, f)))
    filenames.remove(largest_file)  # remove the largest file from the list
                
    # Move all other files to 'extras'
    for filename in filenames:
        if not os.path.isdir(os.path.join(dir, "extras")):
            os.mkdir(os.path.join(dir, "extras"))

        shutil.move(os.path.join(dir, filename), os.path.join(dir, "extras"))

        log(f"Moved {filename} to extras in {dir}")


def scan_movies(dir: str) -> None:
    try:
        dirnames: list[str] = [entry for entry in os.listdir(dir) if os.path.isdir(os.path.join(dir, entry))]

        for dirname in dirnames:
            if os.path.isdir(os.path.join(dir, dirname, "extras")):
                continue

            move_files_except_largest(os.path.join(dir, dirname))

            log(f"Formatted {dirname} in {dir}.")

        log(f"Scan complete for {dir}.")

    except Exception as e:
        with open(f"./logs/{datetime.now().strftime('%Y-%m-%d')}.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')}: Error occured: {e}\n")


@app.route("/update", methods=["GET"])
def update():
    scan_movies(root_dir)

    log("Manually updated movies via /update web call")

    return "Scan complete"


if __name__ == "__main__":
    with open("movie-path.txt", "r") as f:
        root_dir = f.read().strip()

    app.run(port=6845)
    
    schedule.every().day.at("00:00").do(scan_movies, root_dir)

    while True:
        schedule.run_pending()
        sleep(1)