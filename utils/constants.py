# Constants related to YouTube. 
# These have been separated from the rest of the code to make
# updating the scraper easier, whenever YouTube changes the name
# of an element.

### HTML element selector constants
# Selectors used by the data scraper
CSS_LIKES = "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button > div.cbox.yt-spec-button-shape-next--button-text-content > span"
CSS_CHANNEL_RENDERER = "#contents > ytd-channel-renderer"
CSS_CHANNEL_LINK = "#avatar-section > a"
CSS_CHANNEL_SUBSCRIBER_COUNT = "#video-count"
CSS_THUMBNAIL = "#thumbnail"
CSS_VIDEO_TITLE = "#video-title"
CSS_VIDEO_VIEW_COUNT = "#count > ytd-video-view-count-renderer > span.view-count.style-scope.ytd-video-view-count-renderer"
CSS_UPLOAD_DATE = "#info-strings > yt-formatted-string"
CSS_VIDEO_TAGS = 'meta[name="keywords"]'
CSS_CHANNEL_ELEMENT = "#text > a"
CSS_CHANNEL_VIEW_COUNT = "#right-column > yt-formatted-string:nth-child(3)"
CSS_VIDEO_VIEW_COUNT_RENDERER = "#count > ytd-video-view-count-renderer > span.view-count.style-scope.ytd-video-view-count-renderer"
CSS_VIDEO_AGE = '#metadata-line > span:nth-child(2)'
CSS_THUMBNAIL_LINK = "a#thumbnail"
TAG_VIDEO_LIST = "ytd-video-renderer"

# Selectors used by the query scraper
CSS_SEARCH_SUGGESTION = "div.sbqs_c"
CSS_SEARCH_BAR = "input#search"


### URL parameters used to specify search options in YouTube
FOUR_WEEKS_AGO_SEARCH = "&sp=EgIIBA%253D%253D"
ONE_YEAR_AGO_SEARCH = "&sp=EgIIBQ%253D%253D"
CHANNEL_SEARCH = "&sp=EgIQAg%253D%253D"