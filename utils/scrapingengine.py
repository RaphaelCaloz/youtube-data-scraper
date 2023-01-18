import urllib.request
from datetime import date

from selenium.webdriver.common.by import By

from utils import scrapingtools as st
from utils import constants
import csv
import os
import traceback
import pandas as pd
import sys
import json

import pickle

class ScrapingFileLoader:
    def __init__(self):
        self.visited_urls = set()
        self.queries = []
        self.words = []
        self.num_desired_queries = 0
        self.word_index = 0

    def get_visited_urls(self):
        return self.visited_urls
    
    def get_queries(self):
        return self.queries

    def get_num_desired_queries(self):
        return self.num_desired_queries

    def get_words(self):
        return self.words
    def get_word_index(self):
        return self.word_index

    def setup_data_scraping_files(self):
        # Load queries from file and create a list of queries
        if os.path.isdir("./data/non_image_scrape") == False:
            os.mkdir("./data/non_image_scrape")

        with open('./data/non_image_scrape/queries_cleaned.txt', 'r', encoding='utf-8') as f:
            query_lines = f.readlines()
            queries = [query.strip() for query in query_lines]

        if not os.path.isdir("./data/scraper"):
            os.mkdir("./data/scraper")
        if os.path.isdir("./data/images") == False:
            os.mkdir("data/images")

        # Initialize csv file that will contain non-image data, if it doesn't exist.
        # If non image data file does not exist, create it and append
        # the header to it
        if os.path.isfile('./data/non_image_scrape/data.csv') == False:
            with open('./data/non_image_scrape/data.csv', 'a', newline='', encoding='utf-8') as data_obj:
                csv_writer = csv.writer(data_obj)
                csv_writer.writerow([
                    'videoTitle',
                    'videoUrl',
                    'thumbnailUrl',
                    'numViews',
                    'numLikes',
                    'channelName',
                    'totalChannelViews',
                    'numChannelSubscribers',
                    'videoTags',
                    'scrapeDate',
                    'uploadDate'
                ])

        # Load/create hashset that will be used to check if a video has been scraped
        # by storing video URLs.
        if os.path.isfile('./data/scraper/visited_urls.pkl'):
            with open('./data/scraper/visited_urls.pkl', 'rb') as f:
                self.visited_urls = pickle.load(f)

        # Preprocessing  
        self.queries = st.format_queries(queries)

    def setup_query_scraping_files(self):
        if not os.path.isdir("./data/scraper"):
            os.mkdir("./data/scraper")
        if not os.path.isdir("./data/non_image_scrape"):
            os.mkdir("./data/non_image_scrape")

        if os.path.isfile('./data/scraper/query_scraper_checkpoint.json'):
            with open('./data/scraper/query_scraper_checkpoint.json', 'r') as f:
                scraper_variables = json.load(f)
                self.word_index = scraper_variables['current_word_index']
                self.num_desired_queries = scraper_variables['num_desired_queries']
        else:
            print('Enter the total number of search terms you would like to scrape:')
            try:
                self.num_desired_queries = int(input())
                if self.num_desired_queries < 0:
                    raise Exception
            except:
                traceback.print_exc()
                sys.exit("Input must be a valid positive integer.")
            self.word_index = 0
            st.save_query_scraper_variables(self.word_index, self.num_desired_queries)

        with open('data/non_image_scrape/queries.txt', 'a+', encoding='utf-8') as f:
            f.close()

        df = pd.read_csv(
                'data\\preexisting_datasets\\unigram_freq.csv',
                na_filter=False
            )

        # Up to 14 search suggestions can be collected per word in "words"
        self.words = df['word'].tolist()

        

class DataScraper:
    def __init__(self, driver, visited_urls: dict):
        self.driver = driver
        self.visited_urls = visited_urls
        self.last_visited_url = ''

    def get_last_visited_url(self):
        return self.last_visited_url

    def scrape_one_video(self, query, num_thumbnails, query_index):
        # Search youtube for the query with a URL parameter to specify that we want to search
        # for videos uploaded 8-12 months ago.
        self.driver.get(f'https://www.youtube.com/results?search_query={query}{constants.ONE_YEAR_AGO_SEARCH}')

        # Scroll down to load more videos
        st.reliable_scroll_down(self.driver)

        # Skip queries with less than 20 results
        if not st.wait_for_element_to_load(
                self.driver, 
                constants.TAG_VIDEO_LIST, 
                min_elements=20, 
                raise_exception=False, 
                max_get_attempts=200
            ):
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (less than 20 results): ", query, f"(idx: {query_index})")
            return False  # Skip current query, move on to next one

        videos = self.driver.find_elements(by=By.TAG_NAME, value=constants.TAG_VIDEO_LIST)

        video_to_click = -1
        for i, vid in enumerate(videos):
            if (
                not st.is_short(vid)
                and vid.find_element(By.CSS_SELECTOR, value=constants.CSS_THUMBNAIL).get_attribute('href') not in self.visited_urls
            ):
                video_to_click = i
                break
        if video_to_click == -1:
            # Scroll down the page to load more videos
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (no video matches criteria): ", query)
            return False  # Skip current query, move on to next one

        # Scroll the video into view
        self.driver.execute_script("arguments[0].scrollIntoView();", videos[video_to_click])

        # Get the video's title
        video_title = videos[video_to_click].find_element(by=By.CSS_SELECTOR, value=constants.CSS_VIDEO_TITLE).get_attribute('title')

        # Go to the selected video's URL after storing it
        video_url = videos[video_to_click].find_element(By.CSS_SELECTOR, value=constants.CSS_THUMBNAIL).get_attribute('href')
        self.driver.get(video_url)

        # Get the video's thumbnail URL
        video_id = video_url.split('=')[-1]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        backup_thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        # Wait for the video to load
        if not st.wait_for_element_to_load(self.driver, constants.CSS_VIDEO_VIEW_COUNT_RENDERER, raise_exception=False):
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (video did not load in time): ", query)
            return False # Skip current query, move on to next one

        # Get the video's views
        views_element = self.driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_VIDEO_VIEW_COUNT)
        views = st.metadata_str2int(views_element.get_attribute('innerHTML'))

        if views == None:
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (views=None): ", query)
            return False

        # Get the video's likes
        likes = self.driver.find_elements(by=By.CSS_SELECTOR, value=constants.CSS_LIKES)
        if not likes:
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (likes=None): ", query)
            return False  # Skip current query, move on to next one
        likes = likes[0].get_attribute('innerHTML')
        likes = st.metadata_str2int(likes)

        # Get video upload date
        upload_date_element = self.driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_UPLOAD_DATE)
        upload_date = upload_date_element.get_attribute('innerHTML')

        # Get the video's tags
        video_tags = self.driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_VIDEO_TAGS).get_attribute('content')
        if '`' in video_tags:
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (invalid char in tags): ", query)
            return False  # Skip current query, move on to next one

        # Get channel name
        channel_element = self.driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_CHANNEL_ELEMENT)
        channel_name = channel_element.get_attribute('innerHTML')

        # Go to the channel page's about section
        channel_url = channel_element.get_attribute('href')
        self.driver.get(channel_url+'/about')
        if not st.wait_for_element_to_load(self.driver, constants.CSS_CHANNEL_VIEW_COUNT, raise_exception=False):
            print("Skipped query (channel page failed to load): ", query)
            self.skip_query(num_thumbnails, query_index)
            return False # Skip current query, move on to next one

        # Get the channel's total views
        channel_views = self.driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_CHANNEL_VIEW_COUNT).get_attribute('innerHTML')
        channel_views = st.metadata_str2int(channel_views)
        if channel_views == None:
            print("Skipped query (channel_views=None): ", query)
            self.skip_query(num_thumbnails, query_index)
            return False # Skip current query, move on to next one

        # Search for the channel in the search bar
        channel_id = channel_url.split('/')[-1]
        self.driver.get(f'https://www.youtube.com/results?search_query={channel_id}+{channel_name}{constants.CHANNEL_SEARCH}')

        if not st.wait_for_element_to_load(self.driver, constants.CSS_CHANNEL_SUBSCRIBER_COUNT, raise_exception=False):
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (video count failed to load): ", query)
            return False # Skip current query, move on to next one

        channel_renderers = self.driver.find_elements(by=By.CSS_SELECTOR, value=constants.CSS_CHANNEL_RENDERER)

        matching_cr = None

        for cr in channel_renderers:
            cr_href = cr.find_element(by=By.CSS_SELECTOR, value=constants.CSS_CHANNEL_LINK).get_attribute('href').split('/')[-1]
            if cr_href == channel_id:
                matching_cr = cr
                break
            
        if matching_cr == None:
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query (no channel renderer that matches video's channel): ", query)
            return False  # Skip current query, move on to next one

        # Get number of channel subscribers
        channel_subscribers = self.driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_CHANNEL_SUBSCRIBER_COUNT).get_attribute('innerHTML')
        if channel_subscribers == '':  # If channel sub count is hidden
            self.skip_query(num_thumbnails, query_index)
            print("Skipped query 11: ", query)
            return False  # Skip current query, move on to next one
        channel_subscribers = st.metadata_str2int(channel_subscribers)
        if channel_subscribers == None:
            print("Skipped query (channel_subscribers=None): ", query)
            self.skip_query(num_thumbnails, query_index)
            return False # Skip current query, move on to next one

        # Get date at which the video was scraped
        scrape_date = date.today().strftime("%d/%m/%Y")

        # Save the image to the data folder
        try:
            urllib.request.urlretrieve(thumbnail_url, "./data/images/"+st.get_image_name(num_thumbnails))
        except urllib.error.HTTPError:
            try:
                urllib.request.urlretrieve(backup_thumbnail_url, "./data/images/"+st.get_image_name(num_thumbnails))
                thumbnail_url = backup_thumbnail_url
            except urllib.error.HTTPError:
                self.skip_query(num_thumbnails, query_index)
                print("Skipped query (HTTP error when requesting thumbnail): ", query)
                return False  # Skip current query, move on to next one

        self.last_visited_url = video_url

        video_data = [
            video_title,
            video_url,
            thumbnail_url,
            views,
            likes,
            channel_name,
            channel_views,
            channel_subscribers,
            video_tags,
            scrape_date,
            upload_date
        ]

        processed_video_data = self.preprocess_video_data(video_data)

        return processed_video_data
    
    def preprocess_video_data(self, video_data):
        # Prepare the data to be saved as CSV (escape commas, etc)
        processed_video_data = []
        for video_feature in video_data:
            video_feature = str(video_feature)
            video_feature = video_feature.replace('"', '')
            video_feature = video_feature.replace('\n', '')
            processed_video_data.append(video_feature)
        return processed_video_data
    
    def save_video_data(self, processed_video_data, num_thumbnails, query_index):
        # Append collected data to csv
        with open('./data/non_image_scrape/data.csv', 'a', newline='', encoding='utf-8') as data_obj:
            csv_writer = csv.writer(data_obj)
            csv_writer.writerow(processed_video_data)

        # Add video url to hashset
        self.visited_urls.add(self.get_last_visited_url())
        with open('./data/scraper/visited_urls.pkl', 'wb') as f:
            pickle.dump(self.visited_urls, f)

        st.save_data_scraper_variables(num_thumbnails+1, query_index+1)

    # def get_scraping_progress(self):
    #     return st.load_data_scraper_variables()
    
    def skip_query(self, num_thumbnails, query_index):
        st.save_data_scraper_variables(num_thumbnails, query_index+1)