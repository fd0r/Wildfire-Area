import geopandas as gpd
import pandas as pd
import pyproj
from pyproj import Proj
from shapely.ops import transform
from functools import partial
import numpy as np

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


def transform_shapes_projection(shapes, in_espg='2154', out_espg='4326'):
    # Transform shapes coordinates from one projection to another
    proj = partial(pyproj.transform, Proj('epsg:'+in_espg), Proj('epsg:'+out_espg))
    new_shapes = []
    for shape in shapes:
        new_shape = transform(proj, shape)
        new_shape = transform(lambda *x: x[::-1], new_shape)
        new_shapes.append(new_shape)
    return new_shapes

def compute_intersections(gpd_in, gpd_out, in_values, column_in, column_out):
    # Compute intersections beetween geometries from gpd_in and gpd_out, and return
    # a dataframe which associates for each instance of in_values in the column_in 
    # of gpd_in, an array of tuples listing the column_out values of gpd_out which intersect
    # the corresponding geometry in gpd_in
    gpd_in_filtered = gpd_in[gpd_in[column_in].isin(in_values)][['geometry', column_in]]
    intersections = gpd_in_filtered.apply(
        lambda x: extract_intersections(x, gpd_out, column_in, column_out),
        axis=1,
        result_type='expand')
    return intersections.rename(columns={0: 'dep', 1: 'intersections'}).set_index('dep')

def extract_intersections(gpd_in_elem, gpd_out, column_in, column_out):
    # For an element (line) of gpd in, extracts what values in column_out of gpd_out intersects
    # the geometry of the element, and return their intersections
    intersec_tuples = []
    for value, geom in gpd_out[[column_out, 'geometry']].to_numpy():
        if gpd_in_elem['geometry'].intersects(geom):
            intersection = gpd_in_elem['geometry'].intersection(geom)
            intersec_tuples.append((value, intersection.area, intersection))
    return (gpd_in_elem[column_in], intersec_tuples)


def preprocess_DFCI_coordinates(fires, squares_per_dep):
    # Function used to preprocess the DFCI coordinates of the fires data. For a lot of of them,
    # they are not valid, or lower cased.
    valid_letters = 'ABCDEFGHKLMN'
    DFCI_tokens = fires['DFCI_coordinate'].copy().str.upper()

    # We compute per department for the process to be faster

    for dep in fires['Department'].unique():
        where = fires['Department'] == dep

        # So we noticed three irregularites it these data. The first is when the coordinates only
        # miss the last character, an integer between 1 and 5. We locate these error by lookiing at
        # the before last character of the coordinate. The square 5 takes 1/4 of the remaining space
        # (2km^2), and the other have the same area.
        first_case = (where) & (DFCI_tokens.str[-2].str.isalpha())
        randoms_first_case = np.random.rand(len(DFCI_tokens[first_case]), 2)
        new_tokens = 5*np.ones(len(DFCI_tokens[first_case]))
        new_tokens[randoms_first_case[:, 0] > 1/4] = (4*randoms_first_case[randoms_first_case[:, 0] > 1/4, 1]).astype(int)+1
        DFCI_tokens[first_case] = [v + str(t) for v, t in zip(DFCI_tokens[first_case].values, new_tokens.tolist())]

        # The second case is less observed, and is when we only have the 4 first characters of the coordinate.
        # Then we put it in the middle of the square 20*20km square in which it was located
        second_case = (where) & (DFCI_tokens.str.len() == 4)
        DFCI_tokens[second_case] = [v + 'E53' for v in DFCI_tokens[second_case].values]

        # The third case is more complicated. Coordinates from before 1983 are for most of them wrong.
        # They contains letters not referenced in the coordinate system. But we have the department.
        # So in order to give it an exact location, we assign to these fires locations drawn randomly
        # in the departmenent. To do this, we need the shapes of the departmenents and the shapes of the
        # big squares 100*100km of the DFCI coordinate system. Then we compute their intersections and
        # we can draw uniformly in the departement according to the part of the area covered by each big
        # square
        third_case = (where) & (DFCI_tokens.str.len() != 7)
        possible_squares_dep = squares_per_dep.loc[dep]['intersections']
        squares, probas, intersecs = list(zip(*possible_squares_dep))
        square_ids = np.random.choice(
            np.arange(0, len(probas)), size=len(DFCI_tokens[third_case]),
            p=np.array(probas)/sum(probas))
        DFCI_tokens[third_case] = draw_random_dfci_coordinate_in_inter(squares, intersecs, square_ids)
        print('Finished for department ' + dep)
    return DFCI_tokens


def draw_random_dfci_coordinate_in_inter(squares, intersecs, square_ids):
    # This function draw random DFCI coordinates in squares, for point within the
    # corresponding intersections, and the square_ids provide from which square to
    # draw each time
    sorted_ids = np.sort(square_ids)
    valid_letters = 'ABCDEFGHKL'
    unique_idx = np.unique(sorted_ids)
    all_points = []

    # For each square, we compute random point within it and the intersection
    for idx in unique_idx:
        where = sorted_ids == idx
        square = squares[idx]
        intersec = intersecs[idx]
        points = []
        # While the points do not contain enough coordinates
        while(len(points) < len(sorted_ids[where])):
            # We draw a certain number of random coordinates
            how_many = max(int(10000/len(sorted_ids[where])), 1) * len(sorted_ids[where])
            randoms = np.random.rand(how_many, 5)
            dfci_coordinate_0 = [square for i in range(how_many)]
            dfci_coordinate_1 = (5*randoms[:, 0]).astype(int) * 2
            dfci_coordinate_2 = (5*randoms[:, 1]).astype(int) * 2
            dfci_coordinate_3 = [valid_letters[i]
                                 for i in (10*randoms[:, 2]).astype(int)]
            dfci_coordinate_4 = (10*randoms[:, 3]).astype(int)
            dfci_coordinate_5 = (5*randoms[:, 4]).astype(int) + 1
            dfci_coordinates = [a + str(b) + str(c) + d + str(e) + str(f) for a, b, c, d, e, f in zip(dfci_coordinate_0,
                                                                                                      dfci_coordinate_1,
                                                                                                      dfci_coordinate_2,
                                                                                                      dfci_coordinate_3,
                                                                                                      dfci_coordinate_4,
                                                                                                      dfci_coordinate_5)]
            
            # Here we convert them to wgs coordinates
            lat, lon = dfci_to_wgs(dfci_coordinates)

            # We finally add the coordinates for which the corresponding point is in the intersection
            points += [dfci_coord for i, dfci_coord in enumerate(
                dfci_coordinates) if intersec.contains(Point(lon[i], lat[i]))]
        
        # We add as many point as we need
        all_points += points[:len(sorted_ids[where])]

        # We shuffle the result so it is not ordered by square
        np.random.shuffle(all_points)
    return all_points
