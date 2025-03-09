#!/usr/bin/env python3
"""
Twitter/X Post Cleaner - Automatically delete tweets, retweets, and replies
"""

import time
import datetime
import logging
import argparse
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("twitter_cleaner.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TwitterCleaner")

# Default configuration (will be overridden by config.py if available)
TWITTER_USERNAME = ""  # Set in config.py
TWITTER_PASSWORD = ""  # Set in config.py
CHROME_DRIVER_PATH = ""  # Path to chromedriver executable
HEADLESS = False  # Run browser in headless mode
SLEEP_BETWEEN_ACTIONS = 1  # Seconds to wait between actions
MAX_TWEETS_TO_DELETE = 100  # Maximum number of tweets to delete
DEBUG_MODE = False  # Enable additional debug output

# Try to load configuration from config.py
try:
    from config import (
        TWITTER_USERNAME, TWITTER_PASSWORD, CHROME_DRIVER_PATH,
        HEADLESS, SLEEP_BETWEEN_ACTIONS, MAX_TWEETS_TO_DELETE,
        DEBUG_MODE
    )
except ImportError:
    logger.warning("config.py not found. Please create one using config.example.py as a template.")
    if not TWITTER_USERNAME or not TWITTER_PASSWORD:
        logger.error("Twitter/X credentials not set! Please set them in config.py or via command line arguments.")
        sys.exit(1)

def log_time(action, start_time):
    """Log the time taken for an action"""
    end_time = time.time()
    elapsed = end_time - start_time
    logger.info(f"[TIMING] {action}: {elapsed:.3f} seconds")
    return end_time

def enable_performance_options(options):
    """Add performance-enhancing options to the Chrome browser"""
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--dns-prefetch-disable")
    return options

def delete_tweets(username, password, chrome_driver_path, headless=True, sleep_time=0.5, max_delete=float('inf')):
    """Main function to delete tweets, retweets, and replies from a Twitter/X account"""
    try:
        # Start overall timing
        overall_start_time = time.time()
        cycle_start_time = time.time()
        deleted_count = 0
        
        logger.info(f"Starting tweet deletion for user @{username}")
        logger.info(f"Maximum tweets to delete: {max_delete}")
        
        # Set up Chrome driver
        service = Service(executable_path=chrome_driver_path)
        options = ChromeOptions()

        if headless:
            options.add_argument("--headless=new")
            logger.info("Running in headless mode")

        # Configure browser options
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--accept-insecure-certs=true")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # Add performance options
        options = enable_performance_options(options)

        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 5)  # Wait timeout in seconds

        # Log in to Twitter/X
        logger.info("Navigating to login page...")
        time_start = time.time()
        driver.get("https://x.com/login")
        time_start = log_time("Navigate to login page", time_start)

        logger.info("Entering username...")
        time_start = time.time()
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        time_start = log_time("Find username field", time_start)
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        time_start = log_time("Enter username", time_start)
        time.sleep(sleep_time)

        # Handle username verification if needed
        try:
            username_field2 = wait.until(EC.presence_of_element_located((By.NAME, "text")))
            logger.info("Additional username verification required")
            username_field2.send_keys(username)
            username_field2.send_keys(Keys.RETURN)
            time.sleep(sleep_time)
        except:
            pass

        logger.info("Entering password...")
        time_start = time.time()
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        time_start = log_time("Find password field", time_start)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time_start = log_time("Enter password", time_start)
        time.sleep(sleep_time)

        logger.info(f"Page title after login: {driver.title}")
        profile_url = f"https://x.com/{username}"
        logger.info(f"Navigating to profile page: {profile_url}")
        time_start = time.time()
        driver.get(profile_url)
        time_start = log_time("Navigate to profile page", time_start)
        time.sleep(sleep_time)

        # Handle overlays and popups
        try:
            logger.info("Checking for overlays or popups...")
            driver.execute_script("""
                // Remove overlay elements that might intercept clicks
                var overlays = document.querySelectorAll('.r-1habvwh, .r-1xcajam, [role="dialog"]');
                for (var i = 0; i < overlays.length; i++) {
                    overlays[i].style.display = 'none';
                }
                
                // Remove fixed position elements that might be in the way
                var fixed = document.querySelectorAll('.r-fixedPositive, .r-1kihuf0, .r-1upvrn0');
                for (var i = 0; i < fixed.length; i++) {
                    fixed[i].style.display = 'none';
                }
            """)
        except:
            pass
        
        # First navigate to the replies tab to clean those too
        try:
            logger.info("Checking for replies tab...")
            time_start = time.time()
            replies_tab = driver.find_element(By.XPATH, '//a[contains(@href, "/with_replies")]')
            driver.execute_script("arguments[0].click();", replies_tab)
            log_time("Navigate to replies tab", time_start)
            time.sleep(sleep_time)
        except:
            logger.info("Could not find replies tab. Staying on main profile.")
            
        # Scroll to load content
        driver.execute_script("window.scrollBy(0, 300)")
        time.sleep(sleep_time)

        no_tweets_found_count = 0
        
        # Main deletion loop
        while deleted_count < max_delete:
            try:
                logger.info("Finding tweet menu button...")
                tweet_find_start = time.time()
                
                # First check if this is a retweet using its visual indicators
                try:
                    # Look for retweet indicator directly in the timeline
                    retweet_indicator = driver.find_element(By.XPATH, 
                        '//div[contains(@class, "timeline")]//span[contains(text(), "Retweeted") or contains(text(), "retweeted")]')
                    
                    logger.info("Found retweet indicator, looking for its menu...")
                    # Navigate up to the tweet container and then find its menu button
                    tweet_container = retweet_indicator.find_element(By.XPATH, './ancestor::article')
                    retweet_menu_button = tweet_container.find_element(By.CSS_SELECTOR, 'div[data-testid="caret"]')
                    
                    tweet_menu_button = retweet_menu_button
                    logger.info("Found menu button for retweet.")
                except NoSuchElementException:
                    # No retweet indicator found, continue with normal process
                    pass
                
                # Try multiple selectors to locate the tweet menu button
                try:
                    # Try the original selector
                    tweet_menu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="caret"]')))
                except TimeoutException:
                    try:
                        # Alternative selector 1
                        tweet_menu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="More"]')))
                    except TimeoutException:
                        try:
                            # Alternative selector 2 - newer X/Twitter interface
                            tweet_menu_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="More" or @aria-label="More options"]')))
                        except TimeoutException:
                            logger.info("Checking for empty timeline...")
                            # Check if the timeline is empty
                            try:
                                empty_timeline = driver.find_element(By.XPATH, '//*[contains(text(), "hasn\'t posted") or contains(text(), "No posts")]')
                                logger.info("No tweets found. Timeline appears to be empty.")
                                break
                            except NoSuchElementException:
                                # Try refreshing the page
                                logger.info("No menu buttons found. Refreshing the page...")
                                driver.refresh()
                                time.sleep(sleep_time)
                                no_tweets_found_count += 1
                                
                                if no_tweets_found_count >= 3:
                                    logger.info("Unable to find tweets after multiple attempts. Exiting.")
                                    break
                                continue
                
                logger.info("Tweet menu button found. Clicking...")
                log_time("Find tweet menu button", tweet_find_start)
                click_start = time.time()
                # Try JavaScript click instead of regular click to avoid being intercepted
                try:
                    driver.execute_script("arguments[0].click();", tweet_menu_button)
                except:
                    try:
                        tweet_menu_button.click()
                    except:
                        logger.info("Click was intercepted, trying to remove overlays...")
                        # Try to remove any overlays or popups that might be intercepting clicks
                        driver.execute_script("""
                            var elements = document.getElementsByClassName('r-1habvwh');
                            for(var i=0; i<elements.length; i++){
                                elements[i].style.display='none';
                            }
                        """)
                        time.sleep(sleep_time)
                        driver.execute_script("arguments[0].click();", tweet_menu_button)
                
                time.sleep(sleep_time)
                log_time("Click tweet menu button", click_start)

                logger.info("Finding delete button...")
                delete_find_start = time.time()
                try:
                    # Try multiple selectors for the delete button
                    try:
                        delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Delete"]')))
                    except TimeoutException:
                        try:
                            delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Delete")]')))
                        except TimeoutException:
                            try:
                                delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Delete") or contains(text(), "delete")]')))
                            except TimeoutException:
                                # Check for "Undo Retweet" option
                                try:
                                    logger.info("Checking for Undo Retweet option...")
                                    unretweet_time_start = time.time()
                                    # Try multiple ways to find the unretweet option
                                    unretweet_button = None
                                    
                                    # Try method 1: Direct text match
                                    try:
                                        unretweet_button = wait.until(EC.element_to_be_clickable((
                                            By.XPATH, '//span[text()="Undo Retweet" or text()="Unretweet"]')))
                                    except:
                                        # Try method 2: Contains text match
                                        try:
                                            unretweet_button = wait.until(EC.element_to_be_clickable((
                                                By.XPATH, '//span[contains(text(), "Undo") or contains(text(), "unretweet") or contains(text(), "Unretweet")]')))
                                        except:
                                            # Try method 3: Check data-testid attributes
                                            try:
                                                unretweet_button = wait.until(EC.element_to_be_clickable((
                                                    By.CSS_SELECTOR, '[data-testid="unretweet"]')))
                                            except:
                                                # Try method 4: Look for any menu item with 'retweet' in it
                                                try:
                                                    unretweet_button = driver.find_element(By.XPATH, 
                                                        '//*[contains(@class, "menu") or @role="menu"]//span[contains(text(), "retweet") or contains(text(), "Retweet")]')
                                                except:
                                                    pass
                                    
                                    if unretweet_button:
                                        logger.info("Undo Retweet button found. Clicking...")
                                        log_time("Find unretweet button", unretweet_time_start)
                                        
                                        # Use multiple methods to click
                                        try:
                                            driver.execute_script("arguments[0].click();", unretweet_button)
                                        except:
                                            try:
                                                unretweet_button.click()
                                            except:
                                                driver.execute_script(
                                                    "document.evaluate('//span[contains(text(), \"Retweet\")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();")
                                        
                                        time.sleep(sleep_time)
                                    
                                        # Look for confirmation dialog
                                        try:
                                            confirm_time_start = time.time()
                                            confirm_unretweet = None
                                            
                                            # Try multiple ways to find the confirmation button
                                            try:
                                                confirm_unretweet = wait.until(EC.element_to_be_clickable((
                                                    By.XPATH, '//div[@data-testid="unretweetConfirm"]')))
                                            except:
                                                try:
                                                    confirm_unretweet = wait.until(EC.element_to_be_clickable((
                                                        By.XPATH, '//span[contains(text(), "Undo Retweet") or contains(text(), "unretweet")]/ancestor::div[@role="button"]')))
                                                except:
                                                    try:
                                                        confirm_unretweet = driver.find_element(By.XPATH, 
                                                            '//div[contains(@class, "modal") or @role="dialog"]//div[@role="button"][.//span[contains(text(), "Retweet") or contains(text(), "retweet")]]')
                                                    except:
                                                        pass
                                            
                                            if confirm_unretweet:
                                                logger.info("Found confirmation dialog for unretweet. Confirming...")
                                                log_time("Find confirm unretweet button", confirm_time_start)
                                                
                                                # Try different click methods
                                                try:
                                                    driver.execute_script("arguments[0].click();", confirm_unretweet)
                                                except:
                                                    try:
                                                        confirm_unretweet.click()
                                                    except:
                                                        driver.execute_script(
                                                            "document.evaluate('//div[@role=\"dialog\"]//div[@role=\"button\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();")
                                                
                                                time.sleep(sleep_time)
                                                deleted_count += 1
                                                logger.info(f"Unretweeted tweet #{deleted_count}")
                                                continue
                                            else:
                                                logger.info("No confirmation dialog found, but unretweet might still have worked")
                                                deleted_count += 1
                                                logger.info(f"Likely unretweeted tweet #{deleted_count}")
                                                continue
                                        except:
                                            logger.info("Unretweet might have worked without confirmation")
                                            deleted_count += 1
                                            logger.info(f"Possibly unretweeted tweet #{deleted_count}")
                                            continue
                                except:
                                    # Using alternative approach: look for retweet text in the document
                                    try:
                                        logger.info("Using alternative approach to find retweet option...")
                                        
                                        # Try to directly inject a click on any "Retweet" related item
                                        driver.execute_script("""
                                            var menuItems = document.querySelectorAll('[role="menuitem"]');
                                            for (var i = 0; i < menuItems.length; i++) {
                                                if (menuItems[i].textContent.toLowerCase().includes('retweet') || 
                                                    menuItems[i].textContent.toLowerCase().includes('undo')) {
                                                    console.log("Found retweet option, clicking it");
                                                    menuItems[i].click();
                                                    return true;
                                                }
                                            }
                                            return false;
                                        """)
                                        
                                        # Wait a moment to see if a confirmation dialog appears
                                        time.sleep(sleep_time)
                                        
                                        # Try to click any dialog button that appears
                                        driver.execute_script("""
                                            var buttons = document.querySelectorAll('[role="dialog"] [role="button"]');
                                            for (var i = 0; i < buttons.length; i++) {
                                                if (buttons[i].textContent.toLowerCase().includes('retweet') || 
                                                    buttons[i].textContent.toLowerCase().includes('undo')) {
                                                    console.log("Found retweet confirmation, clicking it");
                                                    buttons[i].click();
                                                    return true;
                                                }
                                            }
                                            return false;
                                        """)
                                        
                                        time.sleep(sleep_time)
                                        # Assume it worked
                                        deleted_count += 1
                                        logger.info(f"Used JavaScript injection to unretweet #{deleted_count}")
                                        continue
                                    except:
                                        # None of the options found, close menu and continue
                                        logger.info("No delete or unretweet option found. Closing menu.")
                                        driver.execute_script("document.body.click()")
                                        time.sleep(sleep_time)
                                        driver.execute_script("window.scrollBy(0, 200)")
                                        time.sleep(sleep_time)
                                        continue
                    
                    logger.info("Delete button found. Clicking...")
                    log_time("Find delete button", delete_find_start)
                    delete_click_start = time.time()
                    # Try JavaScript click instead of regular click
                    try:
                        driver.execute_script("arguments[0].click();", delete_button)
                    except:
                        delete_button.click()
                    
                    time.sleep(sleep_time)
                    log_time("Click delete button", delete_click_start)
                except TimeoutException:
                    logger.info("Delete option not found in menu. Checking for reply/retweet options...")
                    
                    # Check for "remove reply" option - for replies
                    try:
                        remove_button = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, '//span[contains(text(), "Remove reply") or contains(text(), "Remove")]')))
                        logger.info("Remove reply button found. Clicking...")
                        driver.execute_script("arguments[0].click();", remove_button)
                        time.sleep(sleep_time)
                        
                        # Confirm removal if needed
                        try:
                            confirm_remove = wait.until(EC.element_to_be_clickable(
                                (By.XPATH, '//div[@data-testid="confirmationSheetConfirm" or contains(@class, "confirm")]')))
                            driver.execute_script("arguments[0].click();", confirm_remove)
                            time.sleep(sleep_time)
                            deleted_count += 1
                            logger.info(f"Removed reply #{deleted_count}")
                            continue
                        except:
                            logger.info("No confirmation dialog for reply removal")
                    except:
                        # If no options are found for this tweet, close the menu and move on
                        logger.info("No delete options found for this tweet. Skipping.")
                        # Try to close any open menus
                        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(sleep_time/2)
                        # Also try clicking away
                        driver.execute_script("document.body.click()")
                        time.sleep(sleep_time/2)
                    
                    # Scroll a bit more and try again
                    driver.execute_script("window.scrollBy(0, 200)")
                    time.sleep(sleep_time)
                    continue

                logger.info("Finding confirm delete button...")
                confirm_find_start = time.time()
                try:
                    # Try multiple selectors for the confirm button
                    try:
                        confirm_delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="confirmationSheetConfirm"]')))
                    except TimeoutException:
                        try:
                            confirm_delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Delete") and (@role="button" or ancestor::button)]')))
                        except TimeoutException:
                            confirm_delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "confirm") or contains(@class, "Confirm")]')))
                            
                    logger.info("Confirm delete button found. Clicking...")
                    log_time("Find confirm button", confirm_find_start)
                    confirm_click_start = time.time()
                    # Try JavaScript click instead of regular click
                    try:
                        driver.execute_script("arguments[0].click();", confirm_delete_button)
                    except:
                        confirm_delete_button.click()
                        
                    time.sleep(sleep_time)  # Reduced wait time after deletion
                    log_time("Click confirm button", confirm_click_start)

                    deleted_count += 1
                    logger.info(f"Deleted tweet #{deleted_count}")
                    
                    # Record total time for this deletion cycle
                    if 'cycle_start_time' in locals():
                        total_cycle_time = time.time() - cycle_start_time
                        logger.info(f"[TIMING] Total deletion cycle time: {total_cycle_time:.3f} seconds")
                    
                    # Start timing the next cycle
                    cycle_start_time = time.time()
                    
                    no_tweets_found_count = 0  # Reset the counter after successful deletion
                    
                except TimeoutException:
                    logger.info("Confirm delete button not found. Might be a UI change.")
                    # Try to press Escape to close any dialogs
                    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(sleep_time)

            except Exception as e:
                logger.warning(f"Error deleting tweet: {type(e)}, {str(e)[:150]}...")  # Only print first 150 chars of error
                
                # Clean up any overlays before trying again
                try:
                    driver.execute_script("""
                        // Remove any elements that might intercept clicks
                        var overlays = document.querySelectorAll('.r-1habvwh, .r-1xcajam, .r-1kihuf0');
                        for (var i = 0; i < overlays.length; i++) {
                            overlays[i].style.display = 'none';
                        }
                    """)
                except:
                    pass
                # Scroll a bit more and continue
                driver.execute_script("window.scrollBy(0, 300)")
                time.sleep(sleep_time)
                no_tweets_found_count += 1
                
                if no_tweets_found_count >= 5:
                    logger.info("Repeated errors encountered. There might be no more tweets to delete.")
                    break

            # Add parallel tweet processing
            try:
                # Try to find multiple tweet menu buttons at once and process them in sequence
                menu_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="caret"]')
                if len(menu_buttons) > 1:
                    logger.info(f"Found {len(menu_buttons)} tweet menu buttons. Processing them sequentially.")
                    # Process the first one in the next iteration
            except:
                pass
                
            # Scroll to load more tweets - more aggressive scrolling
            scroll_start = time.time()
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(sleep_time/2)  # Reduced wait time after scrolling
            log_time("Scroll to load more tweets", scroll_start)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        try:
            driver.quit()
        except:
            pass
        
        # Log overall execution time
        if 'overall_start_time' in locals():
            total_execution_time = time.time() - overall_start_time
            logger.info(f"[TIMING] Total execution time: {total_execution_time:.3f} seconds")
            if deleted_count > 0:
                avg_time_per_tweet = total_execution_time / deleted_count
                logger.info(f"[TIMING] Average time per tweet: {avg_time_per_tweet:.3f} seconds")
        
        logger.info("Script finished.")
        return deleted_count

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Twitter/X Post Cleaner - Delete tweets, retweets, and replies')
    parser.add_argument('-u', '--username', help='Twitter/X username')
    parser.add_argument('-p', '--password', help='Twitter/X password')
    parser.add_argument('-d', '--driver', help='Path to ChromeDriver executable')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('-s', '--sleep', type=float, help='Sleep time between actions (seconds)')
    parser.add_argument('-m', '--max', type=int, help='Maximum number of tweets to delete')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Override config settings with command line arguments if provided
    if args.username:
        TWITTER_USERNAME = args.username
    if args.password:
        TWITTER_PASSWORD = args.password
    if args.driver:
        CHROME_DRIVER_PATH = args.driver
    if args.headless:
        HEADLESS = True
    if args.sleep:
        SLEEP_BETWEEN_ACTIONS = args.sleep
    if args.max:
        MAX_TWEETS_TO_DELETE = args.max
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
        
    # Verify required parameters
    if not TWITTER_USERNAME or not TWITTER_PASSWORD:
        logger.error("Twitter/X username and password are required!")
        sys.exit(1)
    if not CHROME_DRIVER_PATH:
        logger.error("ChromeDriver path is required!")
        sys.exit(1)
        
    # Run the deletion process
    logger.info(f"Starting Twitter/X Post Cleaner for user @{TWITTER_USERNAME}")
    logger.info(f"Configuration: headless={HEADLESS}, sleep={SLEEP_BETWEEN_ACTIONS}, max_delete={MAX_TWEETS_TO_DELETE}")
    
    start_time = time.time()
    deleted = delete_tweets(
        TWITTER_USERNAME, 
        TWITTER_PASSWORD, 
        CHROME_DRIVER_PATH,
        HEADLESS, 
        SLEEP_BETWEEN_ACTIONS, 
        MAX_TWEETS_TO_DELETE
    )
    
    # Final summary
    elapsed = time.time() - start_time
    logger.info(f"Summary: Deleted {deleted} posts in {elapsed:.2f} seconds")
    if deleted > 0:
        logger.info(f"Average time per deletion: {elapsed/deleted:.2f} seconds")
