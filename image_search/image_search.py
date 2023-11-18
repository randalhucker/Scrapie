import os
import csv
import time
from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class ImageSearch:
    FILENAME = "scrapie_search_results"
    WAIT_TIMEOUT = 10

    SELECTORS = {
        "search_by_image_button": '[aria-label="Search by image"]',
        "upload_file_buttons": "//span[contains(text(), 'upload a file')]",
        "image_source_button": '[aria-describedby="reverse-image-search-button-tooltip"]',
        "manage_button": "//div[contains(text(), 'Manage')]",
        "off_button": "//div[contains(text(), ' Off ')]",
        "safe_search_title": "//h1[contains(text(), 'SafeSearch')]",
        "extension_div": "//div[contains(text(), 'More exact matches')]",
        "results_list": '[aria-label="All results list"]',
        "next_upload_button": "//span[contains(text(), 'Upload')]",
        "upload_from_computer": "//span[contains(text(), 'Computer')]",
    }

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.file_counter = 0
        self.current_filename = f"{self.FILENAME}_{self.file_counter}.csv"
        self.wait = WebDriverWait(self.driver, self.WAIT_TIMEOUT)

    def get_initial_source(self) -> None:
        self.navigate_to_google()
        self.click_search_by_image()
        self.upload_image()
        self.disable_safe_search()
        time.sleep(0.5)

    def wait_for_element(self, by, value, timeout=WAIT_TIMEOUT) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_elements(self, by, value, timeout=WAIT_TIMEOUT) -> List[WebElement]:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def navigate_to_google(self) -> None:
        self.driver.get("https://www.google.com/")
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def click_search_by_image(self) -> None:
        search_by_image_button = self.wait_for_element(
            By.CSS_SELECTOR, self.SELECTORS["search_by_image_button"]
        )
        search_by_image_button.click()
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def upload_image(self) -> None:
        upload_buttons: List[WebElement] = self.wait_for_elements(
            By.XPATH, self.SELECTORS["upload_file_buttons"]
        )

        time.sleep(0.1)

        for upload_button in upload_buttons:
            if upload_button.is_displayed():
                upload_button.click()
                break

        image_source_button = self.wait_for_element(
            By.CSS_SELECTOR, self.SELECTORS["image_source_button"], 100
        )

        image_source_button.click()
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def disable_safe_search(self) -> None:
        manage_button = self.wait_for_element(By.XPATH, self.SELECTORS["manage_button"])
        manage_button.click()

        off_button = self.wait_for_element(By.XPATH, self.SELECTORS["off_button"])
        off_button.click()

        title = self.wait_for_element(By.XPATH, self.SELECTORS["safe_search_title"])

        parent_element = title.find_element(By.XPATH, "..")

        first_child_element = parent_element.find_element(By.XPATH, "./*")
        first_child_element.click()

    def open_all_extensions(self):
        while True:
            try:
                extension_div = self.wait_for_element(
                    By.XPATH, self.SELECTORS["extension_div"]
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", extension_div
                )

                span: WebElement = extension_div.find_element(By.XPATH, "..")

                extension_button: WebElement = span.find_element(By.XPATH, "..")
                extension_button.click()
            except Exception as e:
                break

    def get_first_and_second_children(
        self, div_element: WebElement
    ) -> Tuple[WebElement | None, WebElement | None]:
        # Get all child <div> elements within the parent <div>
        children = div_element.find_elements(By.XPATH, "./div")

        # Get the first and second children (if they exist)
        first_child = children[0] if len(children) > 0 else None
        second_child = children[1] if len(children) > 1 else None

        return first_child, second_child

    def get_results(self):
        ul_element = self.wait_for_element(
            By.CSS_SELECTOR, self.SELECTORS["results_list"]
        )

        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        # Print the text content of each <li> element
        for li_element in li_elements:
            a_element = li_element.find_element(By.XPATH, "./a")
            href = a_element.get_attribute("href")
            aria_label = a_element.get_attribute("aria-label")

            if not href or not aria_label:
                continue

            parent_div = li_element.find_element(By.XPATH, "./a/div/div/div/div/div")

            title_child, desc_child = self.get_first_and_second_children(parent_div)

            title = title_child.text if title_child else ""
            desc = desc_child.text if desc_child else ""

            csv_data = {
                "link": href,
                "link_label": aria_label,
                "site_title": title,
                "site_description": desc,
            }

            self.write_to_csv(f"{self.current_filename}", csv_data)

        self.file_counter += 1
        self.current_filename = f"{self.FILENAME}_{self.file_counter}.csv"

    def write_to_csv(self, filename, data):
        file_exists = os.path.isfile(filename)

        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["link", "link_label", "site_title", "site_description"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(data)

    def expand_and_save(self):
        self.open_all_extensions()
        self.get_results()

    def look_for_next_image(self) -> bool:
        try:
            next_upload = self.wait_for_element(
                By.XPATH, self.SELECTORS["next_upload_button"], 100
            )

            if next_upload.text == "Upload":
                next_upload_parent = next_upload.find_element(By.XPATH, "..")
                next_upload_parent.click()

                upload_from_computer = self.wait_for_element(
                    By.XPATH, self.SELECTORS["upload_from_computer"]
                )
                upload_from_computer_parent = upload_from_computer.find_element(
                    By.XPATH, ".."
                )
                current_url = self.driver.current_url
                upload_from_computer_parent.click()

                while self.driver.current_url == current_url:
                    time.sleep(0.1)

                image_source_button = self.wait_for_element(
                    By.CSS_SELECTOR, self.SELECTORS["image_source_button"]
                )
                image_source_button.click()

                return True
            return False
        except Exception as e:
            return False
