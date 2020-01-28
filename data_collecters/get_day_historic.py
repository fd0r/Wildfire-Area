import requests
import os
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
import logging
import sys


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    base_url = "http://www.meteofrance.com/climat/meteo-date-passee?lieuId={code_insee}0&lieuType=VILLE_FRANCE&date={day}-{month}-{year}"
    save_to = "../data/fires_with_meteo.csv"
    base_data = "../data/liste_incendies_ du_10_01_2020.csv"
    if not os.path.exists(save_to):
        fires = pd.read_csv(base_data, sep=";", skiprows=2, low_memory=False)
        fires['date'] = fires['Alerte'].astype("datetime64")
        fires['month'], fires['day'], fires['year'] = \
            fires['date'].dt.month, fires['date'].dt.day, fires['date'].dt.year
        fires['meteo_raw'] = 'TODO'
        logger.info('Using data from {}'.format(base_data))
    else:
        fires = pd.read_csv(
            save_to, sep=";", low_memory=False)
        if sum(fires["meteo_raw"]=="None"):
            fires[fires["meteo_raw"]=="None"] = "NODATA"
        logger.info("Using data from {}".format(save_to))
    logger.info("Data with shape {}".format(fires.shape))


    not_found = 0
    try:
        for index, row in tqdm(fires.iterrows(), total=len(fires)):
            
            rec = str(row['meteo_raw'])
            req = base_url.format(code_insee=str(row['Code INSEE']).upper(
            ).replace('A', '0').replace('B', '0'),  # Handle Corsica
                day=str(row['day']).zfill(2),
                month=str(row['month']).zfill(2),
                year=row['year'])
            
            if not (rec == "TODO"):
                logger.info("Collect not neeed for {}".format(req))
                continue
            
            soup = BeautifulSoup(requests.get(req).text, 'html.parser')
            sub_soup = soup.find('article', {'class': 'report'})
            data = str(sub_soup).replace(";", "")

            if data  != "None":
                fires.loc[index, 'meteo_raw'] = data
            else:
                fires.loc[index, 'meteo_raw'] = "NODATA"
                logging.warn('Data not found for: {}'.format(req))
                not_found += 1

    except Exception as e:
        logger.warning("Program raised error: {}".format(e))
    finally:
        logger.info("Not founds: {}".format(not_found))
        fires.to_csv(save_to, sep=";", index=False)
        logger.info("Data dumped to: {}".format(save_to))
