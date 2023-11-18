from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from image_search import ImageSearch

# CHROMEDRIVER PAGE
# https://googlechromelabs.github.io/chrome-for-testing/

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument("--allow-running-insecure-content")
chromeOptions.add_argument("--ignore-certificate-errors")
chromeOptions.add_argument("--disable-proxy-certificate-handler")
chromeOptions.add_argument("--disable-content-security-policy")
# chromeOptions.add_argument("--headless")

desired_capabilities = DesiredCapabilities.CHROME.copy()
desired_capabilities["acceptInsecureCerts"] = True  # type: ignore


class Driver:
    def __init__(
        self,
        webdriver_path: str,
    ) -> None:
        self.service = Service(webdriver_path)
        self.driver: WebDriver = webdriver.Chrome(
            service=self.service, options=chromeOptions
        )
        self.ImageSearch = ImageSearch(self.driver)
