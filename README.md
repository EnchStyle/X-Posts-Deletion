# Twitter/X Post Cleaner

An automated tool to delete tweets, retweets, and replies from your Twitter/X account.

## Features

- **Bulk Deletion:** Automatically deletes tweets, retweets, and replies
- **Performance Optimized:** Uses direct JavaScript execution for faster interaction
- **Configurable:** Set how many posts to delete and other parameters
- **Retry Logic:** Handles network issues and UI inconsistencies
- **Timing Analytics:** Measures performance at each step
- **Comprehensive Handling:** Works with regular tweets, retweets, and replies

## Requirements

- Python 3.6+
- Selenium WebDriver
- Chrome Browser
- ChromeDriver compatible with your Chrome version

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/twitter-x-post-cleaner.git
   cd twitter-x-post-cleaner
   ```

2. Install the required dependencies:
   ```
   pip install selenium
   ```

3. Download the appropriate [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) for your Chrome version and operating system.

4. Update the `chrome_driver_path` in the script to point to your ChromeDriver location.

## Usage

1. Edit `delete_tweets.py` to add your Twitter/X username and password:
   ```python
   TWITTER_USERNAME = "your_username"
   TWITTER_PASSWORD = "your_password"
   ```

2. Configure the script settings if needed:
   ```python
   HEADLESS = False  # Set to True to run without visible browser
   SLEEP_BETWEEN_ACTIONS = 1  # Seconds to wait between actions
   MAX_TWEETS_TO_DELETE = 100  # Maximum number of tweets to delete
   ```

3. Run the script:
   ```
   python delete_tweets.py
   ```

## Advanced Configuration

### Headless Mode
Set `HEADLESS = True` to run the browser in background mode without displaying a UI. This is useful for servers or automated runs.

### Sleep Duration
Adjust `SLEEP_BETWEEN_ACTIONS` to control how long the script waits between actions. Lower values make it faster but may cause errors if Twitter's interface doesn't load fast enough.

### Maximum Deletions
Set `MAX_TWEETS_TO_DELETE` to limit how many posts will be deleted in a single run.

## Troubleshooting

### Login Issues
- Make sure your username and password are correct
- If you have 2FA enabled, you may need to manually complete the authentication
- Twitter may block automated logins; try running with `HEADLESS = False` to see what's happening

### Element Not Found Errors
- The script has multiple fallbacks for finding elements, but Twitter's UI changes frequently
- Check the console output for timing information to see where it's failing
- Consider increasing `SLEEP_BETWEEN_ACTIONS` if pages aren't loading fast enough

### Intercepted Clicks
- The script attempts to remove overlays and popups that might block clicks
- If you see "click intercepted" errors, try running with the UI visible to see what's happening

## Security Note

This script contains your Twitter/X credentials in plain text. Never share the configured script or upload it to public repositories. This README assumes you're forking the template repository and configuring it privately.

## Performance Tips

The script reports timing for each action. If you see consistently slow steps, consider:

1. Increasing your internet connection speed
2. Reducing `SLEEP_BETWEEN_ACTIONS` if your computer is fast
3. Using a more powerful computer with more RAM
4. Running in headless mode to reduce UI rendering overhead

## Disclaimer

Use this script at your own risk. Automated interaction with Twitter/X may violate their Terms of Service. The script attempts to mimic human behavior, but Twitter may still detect and restrict automated activity.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
