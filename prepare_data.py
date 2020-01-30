import pandas as pd
from sklearn.model_selection import train_test_split

### Load data

fires = pd.read_csv("data/fires.csv", skiprows=2, delimiter=";")

### Transform data

fires.rename(columns={"Année": "Year", "Numéro": "ID", "Type de feu": "Type", "Département": "Department",
                      "Code INSEE": "INSEE_code", "Commune": "Town", "Lieu-dit": "Locality",
                      "Code du carreau DFCI": "DFCI_coordinate", "Alerte": "Signal",
                      "Origine de l'alerte": "Origin", "Surface parcourue (m2)": "Area"},
             inplace=True)
fires.drop(['Type'], axis=1, inplace=True)
fires.loc[fires['Area']==0, 'Area'] = 0.001
fires.loc[fires['Area'].isna(), 'Area'] = 0.001
fires['Signal'] = pd.to_datetime(fires['Signal'], format='%Y-%m-%d %H:%M:%S')
fires.sort_values(['Signal'], ascending=True, inplace=True)

### Split data

date_meteo_1 = pd.Timestamp('1996-01-01')
date_meteo_2 = pd.Timestamp('2010-01-01T01')

prop_test = 0.3

fires_public_1, fires_private_1 = train_test_split(fires[fires['Signal']<date_meteo_1], test_size=prop_test, shuffle=False)
fires_public_2, fires_private_2 = train_test_split(fires[(date_meteo_1<=fires['Signal']) & (fires['Signal']<date_meteo_2)], test_size=prop_test, shuffle=False)
fires_public_3, fires_private_3 = train_test_split(fires[fires['Signal']>=date_meteo_2], test_size=prop_test, shuffle=False)

fires_public_train_1, fires_public_test_1 = train_test_split(fires_public_1, test_size=prop_test, shuffle=False)
fires_public_train_2, fires_public_test_2 = train_test_split(fires_public_2, test_size=prop_test, shuffle=False)
fires_public_train_3, fires_public_test_3 = train_test_split(fires_public_3, test_size=prop_test, shuffle=False)

fires_private_train_1, fires_private_test_1 = train_test_split(fires_private_1, test_size=prop_test, shuffle=False)
fires_private_train_2, fires_private_test_2 = train_test_split(fires_private_2, test_size=prop_test, shuffle=False)
fires_private_train_3, fires_private_test_3 = train_test_split(fires_private_3, test_size=prop_test, shuffle=False)

fires_public_train = fires_public_train_1.append([fires_public_train_2,fires_public_train_3], ignore_index=True)
fires_public_test = fires_public_test_1.append([fires_public_test_2,fires_public_test_3], ignore_index=True)

fires_public_train.to_csv('data/public_train.csv', index=False)
fires_public_test.to_csv('data/public_test.csv', index=False)

fires_private_train = fires_private_train_1.append([fires_private_train_2,fires_private_train_3], ignore_index=True)
fires_private_test = fires_private_test_1.append([fires_private_test_2,fires_private_test_3], ignore_index=True)

fires_private_train.to_csv('data/train.csv', index=False)
fires_private_test.to_csv('data/test.csv', index=False)
