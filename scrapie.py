from selenium_driver import Driver
import sys
import os

if __name__ == "__main__":
    driver = None
    try:
        script_path = os.path.dirname(os.path.abspath(__file__))
        webdriver_path = os.path.join(script_path, "chromedriver.exe")
        driver = Driver(webdriver_path)
        Imager = driver.ImageSearch
        Imager.get_image_sources()
        Imager.open_all_extensions()
        Imager.get_results()
    except Exception as e:
        print(e)
    finally:
        del driver
        sys.exit()
