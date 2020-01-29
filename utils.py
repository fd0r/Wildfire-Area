import geopandas as gpd
import pandas as pd
from pyproj import Proj, transform

def dfci_to_lambert(dfci):
    # Transforms a DFCI square coordinate to the Lambert zone II coordinates of its center
    # See http://ccffpeynier.free.fr/Files/dfci.pdf and http://geofree.fr/gf/projguess.asp
    # for more information
    letters = 'ABCDEFGHKLMN'

    x_lambert = 0
    y_lambert = 1500000

    x_lambert += 100000 * letters.find(dfci[0])
    y_lambert += 100000 * letters.find(dfci[1])

    x_lambert += 20000 * int(dfci[2]) / 2
    y_lambert += 20000 * int(dfci[3]) / 2

    x_lambert += 2000 * letters.find(dfci[4])
    y_lambert += 2000 * int(dfci[5])

    last_idx = int(dfci[6])
    if last_idx == 1:
        x_lambert += 500
        y_lambert += 1500
    elif last_idx == 2:
        x_lambert += 1500
        y_lambert += 1500
    elif last_idx == 3:
        x_lambert += 1500
        y_lambert += 500
    elif last_idx == 4:
        x_lambert += 500
        y_lambert += 500
    else:
        x_lambert += 1000
        y_lambert += 1000

    return x_lambert, y_lambert


def dfci_to_wgs(dfci):
    # Transforms a DFCI square coordinate to the WSG84 coordinates (lat, lon) of its center 
    inProj = Proj('epsg:27572')
    outProj = Proj('epsg:4326')
    lamb_x,lamb_y = dfci_to_lambert(dfci1)
    lat,lon = transform(inProj,outProj,lamb_x,lamb_y)
    return (lat,lon)

def reduce_forest_data(path_forests, path_fires, new_path, new_format='GeoJSON'):
    # Writes a reduced version of the forest geojson data which only contains forests in the same departements
    # as those in which we have fires
    forests = gpd.read_file(path_forests)
    fires = pd.read_csv(path_fires, sep=';',  skiprows=2)

    dep_of_interest = fires['Département'].unique()

    forests_of_interest = forests[forests['cinse_dep'].isin(dep_of_interest)]

    south_east_forests.to_file(new_path, driver=new_format)