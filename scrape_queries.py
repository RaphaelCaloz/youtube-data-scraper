import traceback
import sys

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

from utils import scrapingtools as st
from utils import constants
from utils import scrapingengine

# Setup file hierarchy
scraping_file_loader = scrapingengine.ScrapingFileLoader()
scraping_file_loader.setup_query_scraping_files()

word_index = scraping_file_loader.get_word_index()
num_desired_queries = scraping_file_loader.get_num_desired_queries()
words = scraping_file_loader.get_words()

# Count number of queries that have already been collected
num_queries_collected = st.count_lines('data/non_image_scrape/queries.txt')

# Go to YouTube, get its search bar element
driver = st.create_customized_driver()
driver.get('https://www.youtube.com/')

# This is a workaround. Search suggestions don't show up for the first word inputted 
# into the search bar, so we input a word for which we don't want to scrape 
# auto-suggestions before inputing words from the 'words' list.
st.wait_for_element_to_load(driver, constants.CSS_SEARCH_BAR, wait_interval=0.005)
driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_SEARCH_BAR).clear()
driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_SEARCH_BAR).send_keys('Initialization')

# Collect all 14 search bar suggestions for each word
while num_queries_collected < num_desired_queries and word_index < len(words):
    word = words[word_index]
    try:
        # Clear search bar
        st.wait_for_element_to_load(driver, constants.CSS_SEARCH_BAR, wait_interval=0.005)
        driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_SEARCH_BAR).clear()

        # Input word to search bar
        driver.find_element(by=By.CSS_SELECTOR, value=constants.CSS_SEARCH_BAR).send_keys(word)
        word_index += 1

        # These key strokes are what make search suggestions show up
        ActionChains(driver).key_down(Keys.SPACE).perform()
        ActionChains(driver).key_down(Keys.BACKSPACE).perform()

        # Get search suggestions, skip words with less than 10 search suggestions
        if not st.wait_for_element_to_load(
            driver,
            constants.CSS_SEARCH_SUGGESTION,
            wait_interval=0.05,
            min_elements=10,
            raise_exception=False,
            elem_condition=(lambda elem: word in elem.text)
        ):
            continue  # Skip current word
        search_suggestions = driver.find_elements(by=By.CSS_SELECTOR, value=constants.CSS_SEARCH_SUGGESTION)
        num_queries_collected += len(search_suggestions)
        
        # Truncate last set of search suggestions to scrape exactly the
        # requested number of queries
        if num_queries_collected > num_desired_queries:
            num_ignored_suggestions = num_desired_queries - num_queries_collected
            search_suggestions = search_suggestions[:num_ignored_suggestions]

        # Save current list of search suggestions to queries file
        for search_s in search_suggestions:
            text = search_s.text.replace('\n', '')
            with open('data/non_image_scrape/queries.txt', 'a+', encoding='utf-8') as f:
                f.write(text+'\n')
                f.close()
    except StaleElementReferenceException:
        continue  # Skip current word
    except (selenium.common.exceptions.NoSuchWindowException, KeyboardInterrupt):
        st.save_query_scraper_variables(word_index, num_desired_queries)
        st.clean_queries(
            queries_file_path='./data/non_image_scrape/queries.txt',
            cleaned_file_path='./data/non_image_scrape/queries_cleaned.txt'
        )
        sys.exit(0)  # End program execution if browser window is closed
    except:
        traceback.print_exc()  # Print stack trace
driver.close()
st.save_query_scraper_variables(word_index, num_desired_queries)

if word_index >= len(words):
    print("Ran out of words to input into the search bar before the desired number of search suggestions could be collected.")
else:
    print("Number of requested queries succesfully scraped.")

st.clean_queries(
    queries_file_path='./data/non_image_scrape/queries.txt',
    cleaned_file_path='./data/non_image_scrape/queries_cleaned.txt'
)
