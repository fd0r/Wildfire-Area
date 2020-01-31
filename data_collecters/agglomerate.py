from tqdm import tqdm
import pandas as pd
import os

if __name__ == '__main__':
    path_to_synop = "../data/data_synop"
    csvs_files = [os.path.join(path_to_synop, elt) for elt in os.listdir(path_to_synop)]
    data = pd.DataFrame()
    for file in tqdm(csvs_files):
        try:
            temp = pd.read_csv(file, sep=";", compression=None)
        except pd.errors.EmptyDataError:
            continue
        data = pd.concat([data, temp])
    data.to_csv("../data/synop_aglomerated.csv", index=False)
