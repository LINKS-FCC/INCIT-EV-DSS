from zipfile import ZipFile

import geopandas as gpd
import matplotlib.pyplot as plt
import osgeo.osr as osr
import shapefile
from shapely.geometry import shape


def esri_prj_2_standards(shapeprj_path):
    """
    Given the `.prj` file of the shapefile, it extract:

    1. Well-known text (WKT)
    2. Proj.4 string
    3. ESRI Authority Code

    Parameters
    ----------
    shapeprj_path: str
        path to the `.prj` file of the shapefile

    Returns
    -------
    wkt, proj4, auth_code
        A triplet of numbers:

        1. Well-known text (WKT)
        2. Proj.4 string
        3. ESRI Authority Code
    """
    with open(shapeprj_path, 'r') as f:
        prj_txt = f.read()
    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj_txt])
    srs.AutoIdentifyEPSG()
    return srs.ExportToWkt(), srs.ExportToProj4(), srs.GetAuthorityCode(None)


def shapefile_path_to_geodataframe(filename: str):
    """
    Get GeoDataFrame from a zipfile containing a Shapefile

    Parameters
    ----------
    filename: str
        Zip file of the Shapefile

    Returns
    -------
    gdf: GeoDataFrame
        GeoDataFrame with the information contained in the Shapefile together with geometries.

    """
    shapefile_folder = "./shp/"
    zipfile = ZipFile(filename)
    filenames = [y for y in sorted(zipfile.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)]
    zipfile.extractall(shapefile_folder)
    dbf, prj, shp, shx = [zipfile.open(filename) for filename in filenames]
    zipfile.close()
    r = shapefile.Reader(shp=shp, dbf=dbf, prj=prj, shx=shx)
    wkt, proj4, authority = esri_prj_2_standards(shapefile_folder + prj.name)

    attributes, geometry = [], []
    field_names = [field[0] for field in r.fields[1:]]
    for row in r.shapeRecords():
        geometry.append(shape(row.shape.__geo_interface__))
        attributes.append(dict(zip(field_names, row.record)))
    r.close()
    gdf = gpd.GeoDataFrame(data=attributes, geometry=geometry, crs=proj4)
    gdf = gdf.to_crs("EPSG:4326")
    return gdf


if __name__ == '__main__':
    filename = "circoscrizioni_geo.zip"
    gdf = shapefile_path_to_geodataframe(filename)
    gdf.plot(color="white", edgecolor="black")
    plt.show()
