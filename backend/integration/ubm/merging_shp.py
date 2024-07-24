import os
import zipfile

from ubm.zoning import shapefile_path_to_geodataframe

if __name__ == '__main__':
    filename = "dataset_origin/R01_11_WGS84.zip"
    gdf = shapefile_path_to_geodataframe(filename)
    for com in gdf['COMUNE'].unique():
        gdf_com = gdf[gdf['COMUNE'] == com]
        file_name = com.lower() + '_5T'
        gdf_com.to_file(file_name + '.shp', encoding="utf-8")
        ext = ['.cpg', '.dbf', '.prj', '.shp', '.shx']
        zipf = zipfile.ZipFile('./shapefiles_5T/' + file_name + '.zip', 'w', zipfile.ZIP_DEFLATED)
        for e in ext:
            zipf.write(file_name + e)
        zipf.close()
        for e in ext:
            os.remove(file_name + e)
    pass
