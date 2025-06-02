from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import os

def scrape_jobs_with_selenium(platform, keyword="Software Engineer", location="New York", limit=5, timeout=5):
    """Scrape jobs using a headless browser with a timeout."""
    print(f"Scraping jobs from {platform} using Selenium...")

    driver = None  # Initialize driver to ensure proper cleanup in the `finally` block

    try:
        # Define supported platforms
        supported_platforms = ["indeed"]
        if platform not in supported_platforms:
            print(f"Platform '{platform}' is not supported for scraping.")
            return {"error": f"Platform '{platform}' is not supported."}

        # Scrape jobs from Indeed
        if platform == "indeed":
            base_url = f"https://www.indeed.com/jobs?q={keyword}&l={location}"

            # Set up headless Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
            chrome_options.add_argument("--no-sandbox")  # Disable sandboxing
            chrome_options.add_argument("--disable-dev-shm-usage")  # Use /tmp instead of /dev/shm
            chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
            chrome_options.add_argument("--disable-extensions")  # Disable extensions
            chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
            chrome_options.add_argument("--disable-background-networking")  # Disable background networking
            chrome_options.add_argument("--disable-default-apps")  # Disable default apps
            chrome_options.add_argument("--disable-popup-blocking")  # Disable popup blocking
            chrome_options.add_argument("--disable-translate")  # Disable translation
            chrome_options.add_argument("--disable-sync")  # Disable syncing
            chrome_options.add_argument("--disable-crash-reporter")  # Disable crash reporter
            chrome_options.add_argument("--disable-in-process-stack-traces")  # Disable stack traces
            chrome_options.add_argument("--disable-logging")  # Disable logging
            chrome_options.add_argument("--log-level=3")  # Suppress logs
            chrome_options.add_argument("--output=/dev/null")  # Suppress output

            # Connect to the Selenium container
            selenium_host = os.getenv("SELENIUM_HOST", "selenium")  # Default to 'selenium' container hostname
            selenium_url = f"http://{selenium_host}:4444/wd/hub"  # Selenium Grid URL

            print(f"Connecting to Selenium at {selenium_url}...")

            # Retry mechanism for Selenium connection
            for attempt in range(3):  # Retry up to 3 times
                try:
                    driver = webdriver.Remote(
                        command_executor=selenium_url,
                        options=chrome_options
                    )
                    print("Selenium WebDriver initialized successfully.")
                    break
                except Exception as retry_error:
                    print(f"Attempt {attempt + 1} failed: {retry_error}")
                    time.sleep(2)  # Wait before retrying
            else:
                return {"error": "Failed to connect to Selenium after 3 attempts."}

            # Open the URL
            print(f"Opening URL: {base_url}")
            driver.set_page_load_timeout(timeout)  # Set a timeout for page loading
            try:
                driver.get(base_url)
            except Exception as e:
                print(f"Page load timed out after {timeout} seconds: {e}")
                return {"error": f"Page load timed out after {timeout} seconds."}

            # Parse job listings
            jobs = []
            job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
            print(f"Found {len(job_cards)} job cards. Limiting to {limit} records.")

            # Process only the first `limit` job cards
            for job_card in job_cards[:limit]:
                title = job_card.find_element(By.TAG_NAME, "h2").text.strip() if job_card.find_elements(By.TAG_NAME, "h2") else "N/A"
                company = job_card.find_element(By.CLASS_NAME, "companyName").text.strip() if job_card.find_elements(By.CLASS_NAME, "companyName") else "N/A"
                location = job_card.find_element(By.CLASS_NAME, "companyLocation").text.strip() if job_card.find_elements(By.CLASS_NAME, "companyLocation") else "N/A"
                link = job_card.find_element(By.TAG_NAME, "a").get_attribute("href") if job_card.find_elements(By.TAG_NAME, "a") else "N/A"

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "scraped_at": datetime.utcnow(),
                })

            # Return the scraped jobs
            print(f"Scraping completed. Found {len(jobs)} jobs.")
            return {"success": f"Scraped and stored {len(jobs)} jobs from {platform}.", "jobs": jobs}

    except Exception as e:
        print(f"Error during scraping: {e}")
        return {"error": str(e)}

    finally:
        # Ensure the WebDriver is properly closed in case of an error
        if driver:
            try:
                driver.quit()
                print("WebDriver closed successfully.")
            except Exception as cleanup_error:
                print(f"Error during WebDriver cleanup: {cleanup_error}")