import os
import sys
import time
import atexit
import logging
from selenium_driver import Driver


def setup_driver() -> Driver:
    script_path = os.path.dirname(os.path.abspath(__file__))
    webdriver_path = os.path.join(script_path, "chromedriver.exe")
    return Driver(webdriver_path)


def close_program(driver):
    if driver:
        del driver
        logging.info("Program closed.")


def main():
    driver = None
    try:
        driver = setup_driver()
        imager = driver.ImageSearch
        imager.get_initial_source()

        while True:
            imager.expand_and_save()
            next_image = imager.look_for_next_image()
            if not next_image:
                break

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        atexit.register(close_program, driver)


if __name__ == "__main__":
    main()
