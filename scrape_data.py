import os
import sys
import traceback

import selenium

from utils import scrapingtools as st
from utils import scrapingengine

# Make sure that the query scraper has been run before the data scraper
if not os.path.isfile('data/non_image_scrape/queries.txt'):
    sys.exit("Tried running scrape_data.py before running scrape_queries.py")

# Setup file hierarchy
scraping_file_loader = scrapingengine.ScrapingFileLoader()
scraping_file_loader.setup_data_scraping_files()

# Create chromedriver instance
driver = st.create_customized_driver()

# Initialize the data scraper
data_scraper = scrapingengine.DataScraper(driver, scraping_file_loader.get_visited_urls())

# num_thumbnails: the number of thumbnails that have been scraped
# query_index: the index of the current query in the queries list
num_thumbnails, query_index = st.load_data_scraper_variables()

while query_index < len(scraping_file_loader.get_queries()):
    num_thumbnails, query_index = st.load_data_scraper_variables()
    query = scraping_file_loader.get_queries()[query_index]

    try:
        video_data = data_scraper.scrape_one_video(query, num_thumbnails, query_index)
    except selenium.common.exceptions.NoSuchWindowException:
        sys.exit(0)  # End program execution if browser window is closed
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        traceback.print_exc()  # Print stack trace
        data_scraper.skip_query(num_thumbnails, query_index)
        continue

    if not video_data:
        continue

    data_scraper.save_video_data(video_data, num_thumbnails, query_index)
    
driver.close()