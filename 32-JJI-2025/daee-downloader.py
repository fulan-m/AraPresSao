import os
import sys
import time
import watchdog.events
import watchdog.observers
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

# Estimate number of stations to be downloaded, as of 2023, it was 1696
NUM_REPETITIONS = 1800
DOWNLOAD_DIR = r'download/output/folder/path'

# Uses geckodriver to access the site effectively
# https://github.com/mozilla/geckodriver
GECKODRIVER_PATH = r'folder/path/geckodriver.exe'
TIMEOUT = 70 # Seconds to wait for download completion and to avoid bugs

def create_firefox_profile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    return profile

def download_file(driver, counter):
    # Access the website
    driver.get('http://www.hidrologia.daee.sp.gov.br/')
    time.sleep(10)

    # Set the station type to be selected
    dropdown1 = driver.find_element_by_id('ContentPlaceHolder1_DropDownListTipoDePosto')
    dropdown1.send_keys(Keys.DOWN)
    dropdown1.send_keys(Keys.DOWN)
    time.sleep(10)

    # Set the filter type for station search
    dropdown2 = driver.find_element_by_id('ContentPlaceHolder1_DropDownListTipoDePesquisa')
    dropdown2.send_keys(Keys.DOWN)
    time.sleep(15)

    # Choose the prefixes
    dropdown3 = driver.find_element_by_id('ContentPlaceHolder1_DropDownListPrefixo')
    for _ in range(counter + 1):
        dropdown3.send_keys(Keys.DOWN)
    time.sleep(10)

    # Data type
    dropdown4 = driver.find_element_by_id('ContentPlaceHolder1_DropDownListTipoDeDados')
    dropdown4.send_keys(Keys.DOWN)
    time.sleep(10)

    # Set the starting year
    dropdown5 = driver.find_element_by_id('ContentPlaceHolder1_DropDownListAno')
    dropdown5.send_keys(Keys.DOWN)
    time.sleep(10)

    # Choose download
    download_button = driver.find_element_by_id('ContentPlaceHolder1_ImageButtonExportSerie')
    download_button.click()

def wait_for_download(download_dir, timeout):
    observer = watchdog.observers.Observer()
    handler = Handler()
    observer.schedule(handler, download_dir, recursive=False)
    observer.start()
    start_time = time.time()
    while not handler.download_complete:
        time.sleep(1)
        if time.time() - start_time > timeout:
            print("Download timeout!")
            break
    observer.stop()
    observer.join()

class Handler(watchdog.events.FileSystemEventHandler):
    def __init__(self):
        self.download_complete = False

    def on_created(self, event):
        if not event.src_path.endswith('.part'):
            print(f"Path created: {event.src_path}")
            time.sleep(1)
            self.download_complete = True

def main(counter):
    try:
        for _ in tqdm(range(NUM_REPETITIONS - counter + 1), desc="Repetitions", unit="rep"):
            profile = create_firefox_profile()
            driver = webdriver.Firefox(executable_path=GECKODRIVER_PATH, firefox_profile=profile)
            try:
                download_file(driver, counter)
                wait_for_download(DOWNLOAD_DIR, TIMEOUT)
                counter += 1
            except Exception as e:
                print(f"Error occurred: {e}")
                print(f"Retrying repetition {counter}...")
                time.sleep(10)
                driver.quit()
                continue
            driver.quit()
    except Exception as e:
        print(f"Error occurred: {e}")
        print(f"Re-running script from repetition {counter}")
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    counter = int(input("Enter the starting repetition number: "))
    main(counter)