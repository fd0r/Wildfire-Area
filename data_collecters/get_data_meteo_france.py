import requests
import os
from tqdm import tqdm


if __name__ == "__main__":
    base_url = "https://donneespubliques.meteofrance.fr/donnees_libres/Txt/Synop/Archive/"
    years = range(1996, 2020+1)
    months = range(1, 12+1)
    
    data_folder = "./data/"
    os.makedirs(data_folder, exist_ok=True)
    
    try:
        for year in tqdm(years):
            for month in tqdm(months):
                file_name = "synop.{year}{month}.csv.gz".format(
                    year=str(year), 
                    month=str(month).zfill(2))
                query = "{}{}".format(base_url, file_name)
                response = requests.get(query)
                with open(os.path.join(data_folder, file_name), 'w') as file:
                    file.write(response.text)
    finally:
        print("Dowload done until {}/{}".format(month, year))
