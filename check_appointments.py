from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from enum import Enum
import logging
import logging.config
from log_config import *
import datetime
import sys
import undetected_chromedriver as uc


import httpx
import time
import os

PASSED_OR_NOT_YET = "#c0c0c0"

APPOINTMENTS_AVAILABLE = "#ffffc0"

ALL_TAKEN = "#ADD9F4"


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
year_to_check = 2022
earliest_day = 13


def send_notification(message):
    try:
        api_key = os.environ["PUSHOVER_API_KEY"]
    except KeyError as e:
        logging.error(f"Could not retrieve pushover api key {e}")
    try:
        user_key = os.environ["USER_KEY"]
    except KeyError as e:
        logging.error(f"Could not retrieve user key {e}")

    response = httpx.post(
        "https://api.pushover.net/1/messages.json",
        data={"token": api_key, "user": user_key, "message": message},
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logging.error(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
        )


def main():
    logging.info("Launching headless browser")
    options = uc.ChromeOptions()

    if "darwin" != sys.platform:
        options.add_argument("--headless")

    driver = uc.Chrome(options=options)

    wait = WebDriverWait(driver, 30)
    logging.info("Starting...")
    driver.get("https://evisaforms.state.gov/Instructions/ACSSchedulingSystem.asp")

    country_dropdown = Select(
        wait.until(ec.element_to_be_clickable((By.NAME, "CountryCodeShow")))
    )

    country_dropdown.select_by_visible_text("GREAT BRITAIN AND NORTHERN IRELAND")

    city_dropdown = Select(
        wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "/html/body/form/table/tbody/tr[4]/td[3]/select")
            )
        )
    )

    city_dropdown.select_by_value("LND")

    wait.until(
        ec.element_to_be_clickable(
            (By.XPATH, "/html/body/form/table/tbody/tr[5]/td[3]/input[1]")
        )
    ).submit()
    logging.info("Reached 'Make Appointment'")
    wait.until(
        ec.element_to_be_clickable((By.XPATH, "//input[@value='Make Appointment!']"))
    ).click()
    logging.info("Reached service selection")
    wait.until(ec.element_to_be_clickable((By.XPATH, "//input[@value='AA']"))).click()

    wait.until(
        ec.element_to_be_clickable((By.XPATH, "//input[@name='chkbox01']"))
    ).click()

    wait.until(
        ec.element_to_be_clickable((By.XPATH, "//input[@value='Submit']"))
    ).submit()
    logging.info("Reached calendar")
    month_dropdown = Select(
        wait.until(ec.element_to_be_clickable((By.XPATH, "//select[@name='nMonth']")))
    )

    month_dropdown.select_by_value(month_to_check.value)
    logging.info(f"Checking {month_to_check.name}")

    time.sleep(2)

    appointment_calendar = driver.find_element(
        By.XPATH, value="//*[@id='Table3']/tbody"
    )

    appointment_days = []

    for row in appointment_calendar.find_elements(By.XPATH, value=".//tr"):
        for day in row.find_elements(By.XPATH, value=".//td"):
            # print(day.text)
            day_color = day.get_attribute("bgcolor")
            appointment_day = day.text.replace("\n", ",").split(",")
            if appointment_day[0].isdigit():
                date = int(appointment_day[0])
                if datetime.datetime(year_to_check, int(month_to_check.value), date).weekday() < 5:
                    if ALL_TAKEN == day_color:  # Day with all appointments take
                        logging.info(f"Day: {date:02} - All appointments taken")
                    elif APPOINTMENTS_AVAILABLE == day_color:  # Day with appointments
                        logging.info(f"Day: {date:02} {appointment_day[1]}")
                        if int(day.text.split()[0]) >= earliest_day:
                            appointment_days.append(day.text)
                    elif (
                        PASSED_OR_NOT_YET == day_color
                    ):  # Day passed or no appointments yet
                        logging.info(f"Day: {date:02} - Date passed or not open yet")

    if appointment_days:
        logging.info("Found appointments")
        output = [f"Month: {month_to_check.name} on the {earliest_day} or later."]
        for day in appointment_days:
            day_list = day.replace("\n", ",").split(",")
            output.append(f"Day: {day_list[0]} {day_list[1]}")

        logging.info("\n".join(output))
        logging.info("Sending push notification")
        send_notification("\n".join(output))
    else:
        logging.info(
            f"No appointments for {month_to_check.name} the {earliest_day}th or later"
        )

    time.sleep(5)

    driver.quit()
    logging.info("Done")


if __name__ == "__main__":
    logging.config.dictConfig(LOG_SETTINGS)
    # send_notification("test")
    main()
