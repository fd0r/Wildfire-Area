from pyproj import Proj, transform


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
    lat,lon = transform(inProj,outProj,lamb_x,lamb_y)
    return (lat,lon)