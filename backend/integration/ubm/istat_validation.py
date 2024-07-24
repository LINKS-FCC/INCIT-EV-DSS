import os
import zipfile

from ubm.zoning import shapefile_path_to_geodataframe


def from_istat_to_5t():
    filename = "torino_5T.zip"
    cinque_t = shapefile_path_to_geodataframe(filename)
    filename = "torino_censuaria.zip"
    istat = shapefile_path_to_geodataframe(filename)
    istat['centroid'] = istat['geometry'].centroid
    cinque_t['istat_pop'] = 0
    count_zone = 0
    count_people = 0
    for i, row_i in cinque_t.iterrows():
        mask = istat['centroid'].within(row_i['geometry'])
        count_zone += mask.sum() if mask.any() else 0
        count_people += istat.loc[mask, 'P1'].sum() if mask.any() else 0
        cinque_t.loc[i, 'istat_pop'] += istat.loc[mask, 'P1'].sum()
        if i % 100 == 0:
            print(
                f'{i + 1}/{len(cinque_t)}, counted zone: {count_zone}/{len(istat)}, counted people: {count_people}/{istat.loc[:, "P1"].sum()}')
    cinque_t['istat_pop_ratio'] = cinque_t['istat_pop'] / cinque_t['istat_pop'].sum()
    file_name = 'torino_5T_istat'
    cinque_t.to_file(file_name + '.shp', encoding="utf-8")
    ext = ['.cpg', '.dbf', '.prj', '.shp', '.shx']
    os.makedirs('./torino_5T/')
    zipf = zipfile.ZipFile('./torino_5T/' + file_name + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for e in ext:
        zipf.write(file_name + e)
    zipf.close()
    for e in ext:
        os.remove(file_name + e)



if __name__ == '__main__':
    from_istat_to_5t()
