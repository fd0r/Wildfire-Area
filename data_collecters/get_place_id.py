# TODO: this script should generate the csv with the mapping place to place_id
# Use a selenium bot to do this
# Maybe even just use the autocomplete and not complete a total query

import pandas as pd
from tqdm import tqdm
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

MONTHS = [None, 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
          'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']


class MeteoHistoricScraper:
    def __init__(self):
        super().__init__()
        self.driver = webdriver.PhantomJS()
        self.driver.get("http://www.meteofrance.com/climat/meteo-date-passee")

    def _select_place(self, place, time_to_wait=1):
        place_input = self.driver.find_element_by_id("fcomprer-attr-lieu")
        place_input.send_keys(place)
        time.sleep(time_to_wait)
        place_input.send_keys(Keys.DOWN, Keys.ENTER)

    def _select_date_search(self, year, month, day):
        # Date
        date_input = self.driver.find_element_by_id("fcomprer-attr-date")
        date_input.click()

        selectYear = self.driver.find_element_by_xpath(
            '//select[@class="ui-datepicker-year"]')
        for option in selectYear.find_elements_by_tag_name('option'):
            if option.text == str(year):
                option.click()
                break

        selectMonth = self.driver.find_element_by_xpath(
            '//select[@class="ui-datepicker-month"]')
        for option in selectMonth.find_elements_by_tag_name('option'):
            if option.text == MONTHS[int(month)]:
                option.click()
                break

        selectDay = self.driver.find_element_by_xpath(
            '//table[@class="ui-datepicker-calendar"]')
        for option in selectDay.find_elements_by_xpath('//a'):
            if option.text == str(day):
                option.click()
                break

        date_input.send_keys(Keys.ENTER, Keys.ENTER, Keys.ENTER)

    def get_data(self, place, year, month, day, time_to_wait=1):
        self._select_place(place, time_to_wait)
        self._select_date_search(year, month, day)
        return self.driver.find_element_by_class_name('report').text

    def take_screen(self, screen_name='screen.png'):
        with open(screen_name, 'wb') as image_file:
            image_file.write(self.driver.get_screenshot_as_png())


if __name__ == "__main__":
    fires = pd.read_csv("liste_incendies_ du_10_01_2020.csv",
                        skiprows=2, delimiter=";")
    fires['date'] = fires['Alerte'].astype("datetime64")
    fires['month'], fires['day'], fires['year'] = \
        fires['date'].dt.month, fires['date'].dt.day, fires['date'].dt.year
    fires["raw_meteo"] = ""
    try:
        scraper = MeteoHistoricScraper()
        for idx, fire in tqdm(fires.iterrows(), total=len(fires)):
            try:
                fires.at[idx, "raw_meteo"] = scraper.get_data(
                    fire['Commune'], 
                    fire['year'], 
                    fire['month'], 
                    fire['day']).replace('\n','|')
            except:
                pass
    finally:
        fires.to_csv('fires_with_meteo.csv')
