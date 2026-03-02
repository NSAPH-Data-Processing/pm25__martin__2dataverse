"""
Download PM2.5 NetCDF files from Washington University's Box storage.

This script downloads satellite PM2.5 data from Box using Selenium.
After download, use upload_to_dataverse.py to upload to Harvard Dataverse.
"""

import os
import time
import hydra
import logging
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import shutil

logger = logging.getLogger(__name__)


@hydra.main(config_path="../conf", config_name="config", version_base=None)
def main(cfg):
    """
    Download PM2.5 data from Washington University's Atmospheric Composition Analysis Group.
    https://sites.wustl.edu/acag/datasets/surface-pm2-5/
    """

    # Auto-detect dataset name from loaded config (first key in datasets)
    dataset_name = list(cfg.datasets.keys())[0]
    dataset_cfg = cfg.datasets[dataset_name]
    freq_cfg = dataset_cfg[cfg.temporal_freq]

    url = freq_cfg.box_url
    zipname = freq_cfg.zipname

    # Setup directories
    download_dir = os.path.abspath(f"{cfg.download_dir}/{dataset_name}")
    download_zip = f"{download_dir}/{zipname}.zip"
    src_dir = f"{download_dir}/{zipname}"
    dest_dir = f"{download_dir}/{cfg.temporal_freq}"

    os.makedirs(download_dir, exist_ok=True)

    logger.info(f"Dataset: {dataset_name}")
    logger.info(f"Temporal frequency: {cfg.temporal_freq}")
    logger.info(f"Box URL: {url}")
    logger.info(f"Download directory: {dest_dir}")

    # Set up Chrome options for headless mode and automatic downloads
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "savefile.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    driver = webdriver.Chrome(options=chrome_options)
    logger.info("Chrome driver setup completed.")

    try:
        # Navigate to the website
        driver.get(url)
        driver.refresh()  # Removes popup
        logger.info("Webpage loaded.")

        # Wait for the download button to be clickable
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Download']")
            )
        )

        download_button.click()
        logger.info("Downloading...")

        # Wait for download to complete
        while not os.path.exists(download_zip):
            time.sleep(5)
        logger.info("Download completed.")

        # Unzip contents
        with zipfile.ZipFile(download_zip, "r") as zip_ref:
            zip_ref.extractall(download_dir)

        # Move files to dest_dir, flattening directory structure
        os.makedirs(dest_dir, exist_ok=True)
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                shutil.move(src_file, dest_file)
                logger.info(f"Moved {file} to {dest_dir}")

        # Cleanup
        os.remove(download_zip)
        shutil.rmtree(src_dir)

        # Remove Chrome artifacts
        for file in os.listdir(download_dir):
            if file.startswith("Unconfirmed"):
                os.remove(os.path.join(download_dir, file))

        logger.info("Unzipping completed.")

    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise

    finally:
        driver.quit()
        logger.info("Browser closed.")


if __name__ == "__main__":
    main()
