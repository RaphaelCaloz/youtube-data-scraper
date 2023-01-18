# Project Overview

## Data Scraper

This part of the project navigates YouTube to collect video data (thumbnail images and tabular data). Since YouTube's API greatly limits the number of queries per day, it is not practical to build a dataset with it. This data scraper bypasses the API by simulating a human user navigating the website, collecting data along the way. This makes the collection of a substantial dataset tractable.
<img src="./readme_images/data_scraper_animation.gif" width="720"/>

_The data scraper navigating YouTube._

<br>

## Query Scraper

The query scraper, which was specifically built for this project, collects YouTube auto-suggestions, which the data scraper inputs into the search bar to find videos.
<img src="./readme_images/query_scraper_animation.gif" width="720"/>

_The query scraper collecting search terms._

<br>

# Project Description

## Data Scraper

The data scraper has been designed in a way that makes it easy to update when YouTube's website changes. A single file (`./utils/constants.py`) stores the CSS/Tag selectors for the HTML elements that the scraper interacts with. This way, if YouTube changes the name of an element, or its location on the page, its new selector can be changed in the file, making the program functional in a matter of a few minutes.

Thumbnail images of videos collected are numbered and stored in `./data/images`.

Tabular data collected are stored in `./data/non_image_scrape/data.csv`. Each row of the file holds data from a single YouTube video. The n-th row of data corresponds to the n-th image in `./data/images/`. The columns hold the following information:

- videoTitle: The title of the video.
- videoUrl: The URL of the video.
- thumbnailUrl: The URL of the thumbnail of the video that was saved in the `./data/images/` directory.
- numViews: The number of views the video had at the time it was scraped.
- numLikes: The number of likes the video had at the time it was scraped.
- channelName: The name of the channel that published the video.
- totalChannelViews: The sum of the views on all the videos published by the channel that published the scraped video, at the time it was scraped.
- numChannelSubscribers: The number of subscribers that the channel that published the scraped video had at the time the video was scraped.
- videoTags: The video's tags (keywords that the publisher of the video associated with it to make it easier to find).
- scrapeDate: The date the video was scraped.
- uploadDate: The date the video was uploaded.

## Query Scraper

The query scraper generates queries for the data scraper to use, by following these steps:

1. Input a frequently used english word (read from a file) into YouTube's search bar.
2. Wait for auto-suggestions to load.
3. Scrape the auto-suggestions.
4. Save the scraped data to a file.

Scraped search terms are stored in `./data/non_image_scrape/queries.txt`. Once this file contains the number of queries requested by the user, they will by processed, filtered, and saved to `./data/non_image_scrape/queries_cleaned.txt` (the file that the data scraper uses), and the program execution will end.

<br>

# Installation

1. Clone this repository:

   ```
   $ git clone https://github.com/RaphaelCaloz/youtube-data-scraper.git
   ```

2. Install the required python libraries:

   ```
   $ pip install -r requirements.txt
   ```

3. Replace chromedriver.exe in the project root directory with the version of the ChromeDriver that matches your Google Chrome version. It can be downloaded here: https://chromedriver.chromium.org/downloads

<br>

# How to Run

1. Run `scrape_queries.py`. Enter the number of queries you would like to scrape in the terminal.

2. Run `scrape_data.py`.

Note: Running any of these python files will open a Google Chrome browser window. At any time, the window can be closed to stop the python program without losing scraped data/queries. Alternatively, press `Ctrl+C` in the terminal to exit the program safely.
