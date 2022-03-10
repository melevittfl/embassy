from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from enum import Enum

import undetected_chromedriver as uc


import httpx
import time
import os


class Months(Enum):
    JANUARY = "1"
    FEBRUARY = "2"
    MARCH = "3"
    APRIL = "4"
    MAY = "5"
    JUNE = "6"
    JULY = "7"
    AUGUST = "8"
    SEPTEMBER = "9"
    OCTOBER = "10"
    NOVEMBER = "11"
    DECEMBER = "12"


month_to_check = Months.APRIL


def send_notification(message):
    try:
        api_key = os.environ["PUSHOVER_API_KEY"]
    except KeyError as e:
        print(f"Could not retrieve pushover api key {e}")
    try:
        user_key = os.environ["USER_KEY"]
    except KeyError as e:
        print(f"Could not retrieve user key {e}")

    response = httpx.post(
        "https://api.pushover.net/1/messages.json",
        data={"token": api_key, "user": user_key, "message": message},
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
        )


def main():

    options = uc.ChromeOptions()

    options.add_argument("--headless")

    driver = uc.Chrome(options=options)

    wait = WebDriverWait(driver, 30)

    driver.get("https://evisaforms.state.gov/Instructions/ACSSchedulingSystem.asp")

    country_dropdown = Select(
        wait.until(EC.element_to_be_clickable((By.NAME, "CountryCodeShow")))
    )

    country_dropdown.select_by_visible_text("GREAT BRITAIN AND NORTHERN IRELAND")

    city_dropdown = Select(
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/form/table/tbody/tr[4]/td[3]/select")
            )
        )
    )

    city_dropdown.select_by_value("LND")

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/form/table/tbody/tr[5]/td[3]/input[1]")
        )
    ).submit()

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Make Appointment!']"))
    ).click()

    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='AA']"))).click()

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='chkbox01']"))
    ).click()

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='Submit']"))
    ).submit()

    month_dropdown = Select(
        wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@name='nMonth']")))
    )

    month_dropdown.select_by_value(month_to_check.value)

    time.sleep(2)

    appointment_calendar = driver.find_element(
        By.XPATH, value="//*[@id='Table3']/tbody"
    )

    appointment_days = []

    for row in appointment_calendar.find_elements(By.XPATH, value=".//tr"):
        for day in row.find_elements(By.XPATH, value=".//td"):
            # print(day.text)
            if "#ffffc0" == day.get_attribute("bgcolor"):
                appointment_days.append(day.text)

    if appointment_days:
        output = [f"Month: {month_to_check.name}"]
        for day in appointment_days:
            day_list = day.replace("\n", ",").split(",")
            output.append(f"Day: {day_list[0]} {day_list[1]}")

        print("\n".join(output))
        send_notification("\n".join(output))
    else:
        print(f"No appointments for {month_to_check.name}")

    time.sleep(10)

    driver.quit()


if __name__ == "__main__":
    # send_notification("test")
    main()