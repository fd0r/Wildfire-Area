import requests
import os
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
import logging
import sys
from datetime import timedelta, date


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


if __name__ == "__main__":
    # Logger parameters
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Variables
    base_url = "http://www.meteofrance.com/climat/meteo-date-passee?lieuId={code_insee}0&lieuType=VILLE_FRANCE&date={day}-{month}-{year}"
    data_folder = "../data"
    assert os.path.exists(data_folder)
    save_to = os.path.join(data_folder, "meteo_stations.csv")
    base_data = os.path.join(data_folder, "postesSynop.csv")

    start_date = date(1973, 1, 1)
    end_date = date(2020, 1, 28)
    delta = end_date - start_date
    not_found = 0

    # Data
    df = pd.read_csv(base_data, sep=";")
    df = df[df['interet'] == 'OUI']
    data_total = {
        'date': list(),
        'response': list(),
        'insee_code': list()
    }

    if os.path.isfile(save_to):
        dump = pd.read_csv(save_to, sep=";")
    else:
        dump = pd.DataFrame(columns=['date', 'response', 'insee_code'])
    logger.info(dump.columns)

    try:
        for index, row in tqdm(df.iterrows(), total=len(df)):
            code = row['code_insee']
            sub_data = dump[dump['insee_code'] == int(code.upper(
                ).replace('A', '0').replace('B', '0'))]
            logger.info(
                'found {} elements for insee code={} in already computed data'.format(
                    len(sub_data), code))

            if len(sub_data) == 17193:
                continue

            for single_date in tqdm(daterange(start_date, end_date), 
                                    total=delta.days):

                date_str = single_date.strftime("%Y-%m-%d")

                # could be optimized in two step
                if not sub_data[sub_data['date'] == date_str].empty:
                    continue

                req = base_url.format(code_insee=str(code).upper(
                ).replace('A', '0').replace('B', '0'),  # Handle Corsica
                    day=single_date.strftime("%d").zfill(2),
                    month=single_date.strftime("%m").zfill(2),
                    year=single_date.strftime("%Y"))
                try:  # Handle connection error
                    response = requests.get(req).text
                except requests.exceptions.ConnectionError as connect_error:
                    logger.warning(connect_error, exc_info=True)
                    logger.warning("Error occured for request: {}".format(req))
                    response = ''

                soup = BeautifulSoup(response, 'html.parser')
                sub_soup = soup.find('article', {'class': 'report'})
                data = str(sub_soup).replace(";", "")

                data_total['date'].append(date_str)
                data_total['response'].append(data)
                data_total['insee_code'].append(code)

    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        dump_ = pd.DataFrame(data_total)
        dump = pd.concat([dump, dump_])
        dump.to_csv(save_to, sep=";", index=False)
        logger.info("Data dumped to: {}".format(save_to))
