import geopandas as gpd
import pandas as pd
import pyproj
from pyproj import Proj
from shapely.ops import transform
from functools import partial

def dfci_to_lambert(dfci_coordinates):
    # Transforms a DFCI square coordinate to the Lambert zone II coordinates of its center
    # See http://ccffpeynier.free.fr/Files/dfci.pdf and http://geofree.fr/gf/projguess.asp
    # for more information about how Lambert II and DFCI coordinates work
    # See https://www.promethee.com/doc/prom_donnees.pdf to see how DFCI coordinates are
    # written in the fires data
    letters = 'ABCDEFGHKLMN'
    x_lambert = []
    y_lambert = []
    for i, dfci_coord in enumerate(dfci_coordinates):
        x_lambert.append(0)
        y_lambert.append(1500000)

        x_lambert[i] += 100000 * letters.find(dfci_coord[0])
        y_lambert[i] += 100000 * letters.find(dfci_coord[1])

        x_lambert[i] += 20000 * int(dfci_coord[2]) / 2
        y_lambert[i] += 20000 * int(dfci_coord[3]) / 2

        x_lambert[i] += 2000 * letters.find(dfci_coord[4])
        y_lambert[i] += 2000 * int(dfci_coord[5])

        last_idx = int(dfci_coord[6])
        if last_idx == 1:
            x_lambert[i] += 500
            y_lambert[i] += 1500
        elif last_idx == 2:
            x_lambert[i] += 1500
            y_lambert[i] += 1500
        elif last_idx == 3:
            x_lambert[i] += 1500
            y_lambert[i] += 500
        elif last_idx == 4:
            x_lambert[i] += 500
            y_lambert[i] += 500
        else:
            x_lambert[i] += 1000
            y_lambert[i] += 1000

    return x_lambert, y_lambert


def dfci_to_wgs(dfci_coordinates):
    # Transforms a DFCI square coordinate to the WSG84 coordinates (lat, lon) of its center 
    inProj = Proj('epsg:27572')
    outProj = Proj('epsg:4326')
    lamb_x,lamb_y = dfci_to_lambert(dfci_coordinates)
    lat,lon = pyproj.transform(inProj,outProj,lamb_x,lamb_y)
    return (lat,lon)

def reduce_forest_data(path_forests, path_fires, new_path, new_format='GeoJSON'):
    # Writes a reduced version of the forest geojson data which only contains forests in the same departements
    # as those in which we have fires
    forests = gpd.read_file(path_forests)
    fires = pd.read_csv(path_fires, sep=';',  skiprows=2)

    dep_of_interest = fires['Département'].unique()

    forests_of_interest = forests[forests['cinse_dep'].isin(dep_of_interest)]

    south_east_forests.to_file(new_path, driver=new_format)


def compute_forest_area(forests_shapes):
    # Compute the area in square meters for the forest shapes passed as argument
    areas = []
    proj = partial(pyproj.transform, Proj('epsg:4326'), Proj('epsg:3857'))
    for shape in forests_shapes:
        new_shape = transform(proj, shape)
        areas.append(new_shape.area)
    return areas

def add_forest_areas(path_forests, new_path, new_format='GeoJSON'):
    # Adds a column containing the forests areas and writes it in a new file
    forests = gpd.read_file(path_forests)

    forests['area'] = compute_forest_area(forests['geometry'])

    forests.to_file(new_path, driver=new_format)
