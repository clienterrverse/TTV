import os
import time
import urllib.parse
import argparse
import logging
import sys
from typing import List, Optional
from contextlib import contextmanager

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.service import Service

from retry import retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
CSS_THUMBNAIL = "img.Q4LuWd"
CSS_LARGE = "img.n3VNCb"
CSS_LOAD_MORE = ".mye4qd"
SELENIUM_EXCEPTIONS = (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)

@contextmanager
def create_webdriver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    try:
        yield driver
    finally:
        driver.quit()

def scroll_to_end(wd: webdriver.Chrome):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")

@retry(exceptions=TimeoutException, tries=6, delay=0.1, backoff=2, logger=logger)
def get_thumbnails(wd: webdriver.Chrome, want_more_than: int = 0) -> List[webdriver.remote.webelement.WebElement]:
    scroll_to_end(wd)
    try:
        load_more_button = wd.find_element(By.CSS_SELECTOR, CSS_LOAD_MORE)
        if load_more_button:
            load_more_button.click()
    except NoSuchElementException:
        logger.warning("Load more button not found")
    except (ElementClickInterceptedException, ElementNotInteractableException) as e:
        logger.warning(f"Load more button not clickable: {e}")
    
    thumbnails = wd.find_elements(By.CSS_SELECTOR, CSS_THUMBNAIL)
    if len(thumbnails) <= want_more_than:
        raise TimeoutException("No new thumbnails loaded")
    return thumbnails

@retry(exceptions=TimeoutException, tries=6, delay=0.1, backoff=2, logger=logger)
def get_image_src(wd: webdriver.Chrome) -> List[str]:
    actual_images = wd.find_elements(By.CSS_SELECTOR, CSS_LARGE)
    sources = [img.get_attribute("src") for img in actual_images 
               if img.get_attribute("src").startswith("http") 
               and not img.get_attribute("src").startswith("https://encrypted-tbn0.gstatic.com/")]
    if not sources:
        raise TimeoutException("No large image found")
    return sources

@retry(exceptions=SELENIUM_EXCEPTIONS, tries=6, delay=0.1, backoff=2, logger=logger)
def retry_click(el: webdriver.remote.webelement.WebElement):
    el.click()

def get_images(wd: webdriver.Chrome, n: int = 20, out: Optional[str] = None) -> List[str]:
    thumbnails = []
    while len(thumbnails) < n:
        scroll_to_end(wd)
        try:
            thumbnails = get_thumbnails(wd, want_more_than=len(thumbnails))
        except TimeoutException:
            logger.warning("Cannot load enough thumbnails")
            break

    sources = []
    for tn in thumbnails[:n]:
        try:
            retry_click(tn)
            sources.extend(src for src in get_image_src(wd) if src not in sources)
            if out:
                with open(out, 'a') as f:
                    f.write(f"{sources[-1]}\n")
        except SELENIUM_EXCEPTIONS:
            logger.warning("Failed to get image source", exc_info=True)

        if len(sources) >= n:
            break

    return sources[:n]

def google_image_search(wd: webdriver.Chrome, query: str, safe: str = "off", n: int = 20, opts: str = "", out: Optional[str] = None) -> List[str]:
    search_url = f"https://www.google.com/search?safe={safe}&site=&tbm=isch&source=hp&q={urllib.parse.quote(query)}&oq={urllib.parse.quote(query)}&gs_l=img&tbs={urllib.parse.quote(opts)}"
    wd.get(search_url)
    return get_images(wd, n=n, out=out)

def run_search(query: str, safe: str, n: int, options: str, out: Optional[str] = None) -> List[str]:
    with create_webdriver() as wd:
        return google_image_search(wd, query, safe=safe, n=n, opts=options, out=out)

def main():
    parser = argparse.ArgumentParser(description="Perform a Google image search.")
    parser.add_argument("query", type=str, nargs='?', default="cat", help="Search query (default: 'cat')")
    parser.add_argument("--safe", type=str, default="off", help="Safe search setting")
    parser.add_argument("--n", type=int, default=20, help="Number of images to fetch")
    parser.add_argument("--options", type=str, default="", help="Additional search options")
    parser.add_argument("--out", type=str, default=None, help="Output file path")
    
    args = parser.parse_args()
    
    sources = run_search(args.query, args.safe, args.n, args.options, out=args.out)
    
    for source in sources:
        print(source)

if __name__ == "__main__":
    main()
