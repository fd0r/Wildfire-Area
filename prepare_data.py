import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

### Load data

fires = pd.read_csv("data/fires.csv")

### Transform data

fires.loc[fires['Area']==0, 'Area'] = 0.001
fires.loc[fires['Area'].isna(), 'Area'] = 0.001
fires['Signal'] = pd.to_datetime(fires['Signal'], format='%Y-%m-%d %H:%M:%S')
fires.sort_values(['Signal'], ascending=True, inplace=True)

### Split data

prop_test = 0.25

bins = np.linspace(0,np.log(116000000),25)
inds = np.digitize(np.log(fires['Area'].values),bins)

fires_public, fires_private = train_test_split(fires, test_size=prop_test, shuffle=True,
                                               stratify=inds, random_state=24)

inds_public = np.digitize(np.log(fires_public['Area'].values),bins)
inds_private = np.digitize(np.log(fires_private['Area'].values),bins)

fires_public_train, fires_public_test = train_test_split(fires_public, test_size=prop_test, shuffle=True,
                                                         stratify=inds_public, random_state=7)

fires_private_train, fires_private_test = train_test_split(fires_private, test_size=prop_test, shuffle=True,
                                                           stratify=inds_private, random_state=10)

fires_public_train.to_csv('data/public_train.csv', index=False)
fires_public_test.to_csv('data/public_test.csv', index=False)

fires_private_train.to_csv('data/train.csv', index=False)
fires_private_test.to_csv('data/test.csv', index=False)
