import pandas as pd
from sklearn.model_selection import train_test_split

### Load data

fires = pd.read_csv("data/fires.csv", skiprows=2, delimiter=";")

### Transform data

fires.rename(columns={"Type de feu": "Type", "Code INSEE": "INSEE", "Code du carreau DFCI": "Carreau",
                      "Origine de l'alerte": "Alerteur","Surface parcourue (m2)": "Superficie"},
             inplace=True)
fires['Alerte'] = pd.to_datetime(fires['Alerte'], format='%Y-%m-%d %H:%M:%S')
fires.sort_values(['Alerte'], ascending=True, inplace=True)

### Split data

date_meteo_1 = pd.Timestamp('1996-01-01')
date_meteo_2 = pd.Timestamp('2010-01-01T01')

prop_test = 0.3

fires_public_1, fires_private_1 = train_test_split(fires[fires['Alerte']<date_meteo_1], test_size=prop_test, shuffle=False)
fires_public_2, fires_private_2 = train_test_split(fires[(date_meteo_1<=fires['Alerte']) & (fires['Alerte']<date_meteo_2)], test_size=prop_test, shuffle=False)
fires_public_3, fires_private_3 = train_test_split(fires[fires['Alerte']>=date_meteo_2], test_size=prop_test, shuffle=False)

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
