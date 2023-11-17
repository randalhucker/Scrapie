import os
from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time


class ImageSearch:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.filename = ""

    def get_image_sources(self) -> None:
        self.navigate_to_google()
        self.click_search_by_image()
        self.upload_image()
        self.disable_safe_search()
        time.sleep(0.5)

    def wait_for_element(self, by, value, timeout=10) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_elements(self, by, value, timeout=10) -> List[WebElement]:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def navigate_to_google(self) -> None:
        self.driver.get("https://www.google.com/")
        time.sleep(0.5)

    def click_search_by_image(self) -> None:
        search_by_image_button = self.driver.find_element(
            By.CSS_SELECTOR, '[aria-label="Search by image"]'
        )
        search_by_image_button.click()
        time.sleep(0.5)

    def upload_image(self) -> None:
        upload_buttons: List[WebElement] = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[contains(text(), 'upload a file')]")
            )
        )

        for upload_button in upload_buttons:
            if upload_button.is_displayed():
                upload_button.click()
                break

        image_source_button = self.wait_for_element(
            By.CSS_SELECTOR, '[aria-describedby="reverse-image-search-button-tooltip"]'
        )

        image_source_button.click()
        time.sleep(0.5)

    def disable_safe_search(self) -> None:
        manage_button = self.wait_for_element(
            By.XPATH, "//div[contains(text(), 'Manage')]"
        )

        manage_button.click()

        off_button = self.wait_for_element(By.XPATH, "//div[contains(text(), ' Off ')]")

        off_button.click()

        title = self.wait_for_element(By.XPATH, "//h1[contains(text(), 'SafeSearch')]")

        parent_element = title.find_element(By.XPATH, "..")

        first_child_element = parent_element.find_element(By.XPATH, "./*")

        first_child_element.click()

    def open_all_extensions(
        self,
    ):
        time.sleep(1)
        while True:
            try:
                extension_div = self.wait_for_element(
                    By.XPATH, "//div[contains(text(), 'More exact matches')]"
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", extension_div
                )

                span: WebElement = extension_div.find_element(By.XPATH, "..")
                extension_button: WebElement = span.find_element(By.XPATH, "..")

                extension_button.click()
                time.sleep(0.5)
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
        time.sleep(1)
        ul_element = self.driver.find_element(
            By.CSS_SELECTOR, '[aria-label="All results list"]'
        )

        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        # Print the text content of each <li> element
        for li_element in li_elements:
            href = li_element.find_element(By.XPATH, "./a").get_attribute("href")
            aria_label = li_element.find_element(By.XPATH, "./a").get_attribute(
                "aria-label"
            )

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

            self.write_to_csv(f"{self.filename}.csv", csv_data)

    def write_to_csv(self, filename, data):
        file_exists = os.path.isfile(filename)

        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["link", "link_label", "site_title", "site_description"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if the file is created (doesn't exist)
            if not file_exists:
                writer.writeheader()

            writer.writerow(data)
