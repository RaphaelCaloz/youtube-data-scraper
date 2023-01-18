import os
from time import sleep
import re
import json

import selenium
from selenium.webdriver.common.by import By

from utils import constants

def prt(text, dec='#'):
    print()
    print(dec*20)
    print(text)
    print(dec*20)
    print()
    
def format_queries(qrs):
    qrs = [query.replace(" ", "+") for query in qrs]
    return qrs

def clean_queries(queries_file_path, cleaned_file_path):
    # Remove duplicate queries
    with open(queries_file_path, 'r', encoding='utf-8') as f:
        queries = f.readlines()
        f.close()

    queries = [q.strip() for q in queries]
    queries = list(dict.fromkeys(queries))

    # Remove non ASCII characters from queries
    queries = [q.encode('ascii', 'ignore').decode('ascii') for q in queries]

    # Remove empty lines
    queries = [q for q in queries if q != '']

    # Save cleaned queries to file
    with open(cleaned_file_path, 'w+', encoding='ascii') as f:
        for q in queries:
            f.write(q + '\n')
        f.close()

# This function checks if a WebElement is a youtube short video
def is_short(video: selenium.webdriver.remote.webelement.WebElement):
    return '/shorts/' in video.find_element(By.CSS_SELECTOR, value=constants.CSS_THUMBNAIL_LINK).get_attribute('href')

# This function checks if a WebElement has a publication time and returns it
# This function is useful because certain types of videos (such as live videos) 
# don't have a publication time, which throws an error when trying to get the
# publication time.
def get_video_age(video, not_found_return_value=""):
    if len(video.find_elements(by=By.CSS_SELECTOR, value=constants.CSS_VIDEO_AGE)) == 0:
        return not_found_return_value
    else:
        return video.find_element(by=By.CSS_SELECTOR, value=constants.CSS_VIDEO_AGE).text

def get_video_age_months(video, not_found_return_value=-1):
    if len(video.find_elements(by=By.CSS_SELECTOR, value=constants.CSS_VIDEO_AGE)) == 0:
        return not_found_return_value
    else:
        txt = video.find_element(by=By.CSS_SELECTOR, value=constants.CSS_VIDEO_AGE).text
        if 'months' in txt:
            try:
                return int(txt.split(' ')[0])
            except:
                return not_found_return_value
        else:
            return not_found_return_value

def load_data_scraper_variables():
    '''
    Returns a tuple of saved runtime scrapers variables in a tuple.
    This tuple is: (number_of_thumbnails_scraped, query_index).
    '''
    if not os.path.isdir("data/scraper"):
        os.mkdir("data/scraper")
    
    if os.path.isfile('./data/scraper/data_scraper_checkpoint.json'):
        with open('./data/scraper/data_scraper_checkpoint.json', 'r') as f:
            scraper_variables = json.load(f)
        return (
            scraper_variables['number_of_thumbnails_scraped'],
            scraper_variables['query_index']
            )
    else:
        # Create a new file if it doesn't exist
        with open('./data/scraper/data_scraper_checkpoint.json', 'w') as f:
            json.dump({
                "number_of_thumbnails_scraped": 0, 
                "query_index": 0
                }, f)
        return (0,0)

def save_data_scraper_variables(num_thumbnails, query_index):
    with open('./data/scraper/data_scraper_checkpoint.json', 'w') as f:
        json.dump({
            "number_of_thumbnails_scraped": num_thumbnails, 
            "query_index": query_index
            }, f)

def save_query_scraper_variables(word_index, num_desired_queries):
    with open('./data/scraper/query_scraper_checkpoint.json', 'w') as f:
        json.dump({
            'current_word_index': word_index,
            'num_desired_queries': num_desired_queries
        }, f)

def metadata_str2int(meta: str):
    #if meta is None or not re.match('^[\d\.]+\s*[aA-zZ]*$', meta):
    if meta in ('Like', 'No views', '', None) or re.match('[^aA-zZ\d\s\.\,]+', meta) != None:
        # Write meta to a file
        with open('./data/scraper/metadata_errors.txt', 'w+') as f:
            f.write(meta + '\n')
        return None
    meta = meta.split(' ')[0].replace(',', '')
    if meta[-1] == 'K':
        meta = float(meta[:-1])*1e3
    elif meta[-1] == 'M':
        meta = float(meta[:-1])*1e6
    elif meta[-1] == 'B':
        meta = float(meta[:-1])*1e9
    return int(meta)

def wait_for_element_to_load(browser_driver, css_selector, min_elements=1, wait_interval=0.1, max_get_attempts=50, raise_exception=True, elem_condition=lambda elem: True):
    assert min_elements >= 1
    attempts = 0
    while attempts < max_get_attempts:
        if len(browser_driver.find_elements(by=By.CSS_SELECTOR, value=css_selector)) < min_elements:
            sleep(wait_interval)
            attempts += 1
        else:
            for web_elem in browser_driver.find_elements(by=By.CSS_SELECTOR, value=css_selector):
                if not elem_condition(web_elem):
                    sleep(wait_interval)
                    break
            return True
    if attempts == max_get_attempts:
        if raise_exception:
            raise Exception(f'Element(s) with selector "{css_selector}" did not load in {max_get_attempts} get attempts.')
        return False

def reliable_scroll_down(driver, scroll_height=50000):
    MAX_SCROLL_ATTEMPTS = 10
    attempts = 0
    delta_y = 0

    while delta_y == 0 and attempts < MAX_SCROLL_ATTEMPTS:
        y_before = driver.execute_script("return window.pageYOffset;")
        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        y_after = driver.execute_script("return window.pageYOffset;")
        delta_y = y_after - y_before
        attempts += 1

def get_image_name(thumbnail_index):
    name = str(thumbnail_index)
    num_leading_zeros = 8 - len(name)
    return '0'*num_leading_zeros + name + '.jpg'

def create_customized_driver():
    # Configure chromedriver with audio muted, with cookies blocked and in incognito mode
    chrome_options = selenium.webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--incognito')
    chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": 2})

    # Configure chromedriver to be headless (hide window)
    # chrome_options.add_argument("--headless")

    # Create chromedriver instance
    return selenium.webdriver.Chrome(chrome_options=chrome_options)

def count_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return len(lines)