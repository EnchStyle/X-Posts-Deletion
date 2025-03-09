# Twitter/X Post Cleaner Configuration
# Rename this file to "config.py" and update with your information

# Your Twitter/X credentials
TWITTER_USERNAME = "your_username"
TWITTER_PASSWORD = "your_password"

# Path to ChromeDriver executable
# Example for Windows: "C:/path/to/chromedriver.exe"
# Example for Mac/Linux: "/path/to/chromedriver"
CHROME_DRIVER_PATH = "/path/to/chromedriver"

# Script settings
HEADLESS = False               # Set to True to run without visible browser
SLEEP_BETWEEN_ACTIONS = 1      # Seconds to wait between actions
MAX_TWEETS_TO_DELETE = 100     # Maximum number of tweets to delete (use float('inf') for unlimited)

# Advanced settings (optional)
DEBUG_MODE = False             # Enable additional debug output
SCROLL_AMOUNT = 500            # Pixels to scroll to load more tweets
WAIT_TIMEOUT = 5               # Maximum seconds to wait for elements
AUTO_CLOSE_BROWSER = True      # Close browser when done
