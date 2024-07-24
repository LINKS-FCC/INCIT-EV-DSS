import os
import re

import numpy as np
import rasterio
from geopandas import GeoDataFrame
from rasterio import features
from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject
from rasterio.windows import Window
from shapely.geometry import Polygon

from ubm.plotting import plot_shape_enact_corine_raster
from ubm.utils.stuff import load_yaml

target_crs = 'EPSG:4326'


def raster_to_4326(src_path: str):
    """
    Convert Raster to EPSG:4326

    Parameters
    ----------
    src_path: str
        Path of the raster to be converted.

    """
    name = os.path.splitext(src_path)
    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height,
            "compress": "lzw",
        })

        with rasterio.open(src_path.replace("3035", "4326"), 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest)


def coord_to_data(file_name: str, lng: float, lat: float):
    """
    Query the GeoTIFF file at `file_name` by using coordinates.
    It assumes that `lng` and `lat` has the same CRS of the GeoTIFF file.

    Parameters
    ----------
    file_name: str
        GeoTIFF filename
    lng: float
        longitude
    lat: float
        latitude

    Returns
    -------
    value_geo_tiff: float
        value in the corresponding (lng, lat) point.
    """
    dataset = rasterio.open(file_name)
    # get pixel x+y of the coordinate
    py, px = dataset.index(lng, lat)
    # create 1x1px window of the pixel
    window = Window(px - 1 // 2, py - 1 // 2, 1, 1)
    # read rgb values of the window
    clip = dataset.read(window=window)
    return clip


def generate_day_night_average_year(root_folder_enact: str = "./ENACT_POP_2011_EU28_R2020A/"):
    """
    Routine to generate day and night ENACT_POP values by taking the average on every month available.
    The file will be generate in the root folder as `day.tif` and `night.tif`.

    Parameters
    ----------
    root_folder_enact: str
        folder containing the zipfile of the ENACT_POP dataset extracted.

    """
    day_rasters = []
    night_rasters = []
    metadata = None
    for x in os.listdir(root_folder_enact):
        if os.path.isdir(root_folder_enact + x):
            tif_file_name = root_folder_enact + x + "/" + x + ".tif"
            print(tif_file_name)
            a = re.search("_(?P<ND>[N,D])(?P<month>[0-9]*)_", tif_file_name)
            if a.group("ND") == "D":
                r = rasterio.open(tif_file_name)
                day_rasters.append(r.read())
                if metadata is None:
                    metadata = r.meta
            elif a.group("ND") == "N":
                r = rasterio.open(tif_file_name)
                night_rasters.append(r.read())
    write_to_file(day_rasters, night_rasters, metadata, "day_0311_avg.tif", "night_0311_avg.tif")


def generate_day_night_average_november_march(root_folder_enact: str = "./ENACT_POP_2011_EU28_R2020A/"):
    """
    Routine to generate day and night ENACT_POP values by taking the average on every month available.
    The file will be generate in the root folder as `day.tif` and `night.tif`.

    Parameters
    ----------
    root_folder_enact: str
        folder containing the zipfile of the ENACT_POP dataset extracted.

    """
    day_rasters = []
    night_rasters = []
    metadata = None
    for x in os.listdir(root_folder_enact):
        if os.path.isdir(root_folder_enact + x):
            tif_file_name = root_folder_enact + x + "/" + x + ".tif"
            a = re.search("_(?P<ND>[N,D])(?P<month>[0-9]*)_", tif_file_name)
            if a.group("ND") == "D" and (a.group("month") == "032011" or a.group("month") == "112011"):
                print(tif_file_name)
                r = rasterio.open(tif_file_name)
                day_rasters.append(r.read())
                if metadata is None:
                    metadata = r.meta
            elif a.group("ND") == "N" and (a.group("month") == "032011" or a.group("month") == "112011"):
                print(tif_file_name)
                r = rasterio.open(tif_file_name)
                night_rasters.append(r.read())
    write_to_file(day_rasters, night_rasters, metadata, "day_0311_avg.tif", "night_0311_avg.tif")


def generate_day_night_average_november_march_targeted(
        root_folder_enact: str = "./ENACT_POP_2011_EU28_R2019A_4326_1K_V1_0_LF6POPCLASS/"):
    """
    Routine to generate day and night ENACT_POP values by taking the average on every month available.
    The file will be generate in the root folder as `day.tif` and `night.tif`.

    Parameters
    ----------
    root_folder_enact: str
        folder containing the zipfile of the ENACT_POP dataset extracted.

    """
    day_rasters = []
    night_rasters = []
    dataset_dict = {}
    metadata = None
    for x in os.listdir(root_folder_enact):
        x = root_folder_enact + x
        a = re.search("_(?P<ND>[N,D])(?P<month>[0-9]*)_.*_(?P<target>[A-Z]+)\.tif", x)
        r = rasterio.open(x)
        assert r.crs == target_crs, "CRS problem"
        if metadata is None:
            metadata = r.meta
        if a.group("ND") + a.group("month") not in dataset_dict:
            dataset_dict[a.group("ND") + a.group("month")] = []
        dataset_dict[a.group("ND") + a.group("month")].append(r.read())
    for key in dataset_dict:
        dataset_dict[key] = np.array(dataset_dict[key]).sum(axis=0)
    for key in dataset_dict:
        if key == "D032011" or key == "D112011":
            day_rasters.append(dataset_dict[key])
        if key == "N032011" or key == "N112011":
            night_rasters.append(dataset_dict[key])
    write_to_file(day_rasters, night_rasters, metadata, "day_0311_avg_t.tif", "night_0311_avg_t.tif")


def write_to_file(day_rasters: list, night_rasters: list, metadata, day_str: str, night_str: str):
    """
    Writes day and night raster to filesystem.

    Parameters
    ----------
    day_rasters: list
        List of Day Rasters
    night_rasters:vlist
        List of Day Rasters
    metadata:
        Raster Metadata
    day_str: str
        String to use as output data for day rasters
    night_str: str
        String to use as output data for day rasters
    """
    day_raster_final = np.zeros(day_rasters[0].shape, dtype=rasterio.float64)
    night_raster_final = np.zeros(night_rasters[0].shape, dtype=rasterio.float64)
    for d in day_rasters:
        day_raster_final += d.squeeze()
    for d in night_rasters:
        night_raster_final += d.squeeze()
    # Update metadata
    kwargs = metadata
    kwargs.update(
        dtype=rasterio.float64,
        count=1,
        compress='lzw',
        nodata=-200
    )
    day_raster_final = day_raster_final / len(day_rasters)
    night_raster_final = night_raster_final / len(night_rasters)
    with rasterio.open(day_str, 'w+', **kwargs) as dst:
        dst.write(day_raster_final)
    with rasterio.open(night_str, 'w+', **kwargs) as dst:
        dst.write(night_raster_final)


def add_enact_pop_stat_to_gdf(gdf: GeoDataFrame, prefix="enact_pop_", day_file: str = "./datasets/day_0311_avg_t.tif",
                              night_file: str = "./datasets/night_0311_avg_t.tif",
                              corine_file: str = './datasets/corine.4326.tif', corine_dict_day=None,
                              corine_dict_night=None):
    """
    Takes as input a GeoDataFrame and adds to the dataset the information extracted from ENACT_POP and Corine datasets.

    Parameters
    ----------
    gdf: GeoDataFrame
        GeoDataFrame with geometries that will be used as mask to extract data.
    prefix: str (Optional)
        Prefix to use as columns header.
    day_file: str
        Path to the file that has to be used as DAY.
    night_file: str
        Path to the file that has to be used as NIGHT.
    corine_file: str
        Path to the file that contains the TIFF of the Corine Dataset.

    Returns
    -------
    gdf: GeoDataFrame
        GeoDataFrame filled with data coming from ENACT_POP and Corine datasets.
    """
    if corine_dict_day is None:
        corine_dict_day = load_yaml('./config/corine_day.yaml')
    if corine_dict_night is None:
        corine_dict_night = load_yaml('./config/corine_night.yaml')
    gdf = __extract_jrc_corine_data(gdf, corine_dict_day, day_file, corine_file, prefix, "day")
    gdf = __extract_jrc_corine_data(gdf, corine_dict_night, night_file, corine_file, prefix, "night")
    return gdf


def __extract_jrc_data(gdf: GeoDataFrame, filename: str, prefix="enact_pop_", title="test"):
    """
    Extraction of the data from ENACT_POP, this is a low level function, then we suggest to not use it outside this
    module.

    Parameters
    ----------
    gdf: GeoDataFrame
        GeoDataFrame with geometries that will be used as mask to extract data.
    filename: str
        filename of the GeoTIFF coming from ENACT_POP
    prefix: str (Optional)
        Prefix to use as columns header.
    title: str (Optional)
        title to use as columns header.

    Returns
    -------
    gdf: GeoDataFrame
        GeoDataFrame filled with data coming from ENACT_POP dataset.
    """
    results = []
    for i in range(len(gdf)):
        with rasterio.open(filename) as dataset:
            # Get only the rasters that touches the current shape
            out_image, out_transform = mask(dataset, [gdf.iloc[i].geometry], crop=True, nodata=0, all_touched=True)
            area_sum = 0
            for geometry, raster_value in features.shapes(out_image.astype(np.float32), transform=out_transform):
                squares = Polygon(geometry['coordinates'][0])
                # plot_shape_raster(squares, gdf.iloc[i].geometry)  # Plotting for debugging
                overlapping_poly = squares.intersection(gdf.iloc[i].geometry)
                if not overlapping_poly.is_empty:
                    ratio = overlapping_poly.area / squares.area
                    area_sum += ratio * raster_value
        results.append(area_sum)
    gdf[prefix + title + "_sum"] = results
    gdf[prefix + title + "_ratio"] = gdf[prefix + title + "_sum"] / gdf[prefix + title + "_sum"].sum()
    return gdf


def __extract_jrc_corine_data(gdf: GeoDataFrame, corine_dict: dict, enact_tif: str = "./datasets/night_0311_avg_t.tif",
                              corine_tif: str = './datasets/corine.4326.tif',
                              prefix="enact_corine_",
                              title="test", debug_plot: bool = False):
    """
    Extraction of the data from ENACT_POP and Corine, this is a "low-level" function,
    then we suggest to not use it outside this module.

    Parameters
    ----------
    gdf: GeoDataFrame
        GeoDataFrame with geometries that will be used as mask to extract data.
    corine_dict: dict
        Corine Type to Value Dictionary
    enact_tif: str (Optional)
        filename of the GeoTIFF coming from ENACT_POP
    corine_tif: str (Optional)
        filename of the GeoTIFF coming from Corine Land Use
    prefix: str (Optional)
        Prefix to use as columns header.
    title: str (Optional)
        title to use as columns header.

    Returns
    -------
    gdf: GeoDataFrame
        GeoDataFrame filled with data coming from ENACT_POP dataset.
    """
    corine = rasterio.open(corine_tif)
    night_enact = rasterio.open(enact_tif)
    results = []
    for i in range(len(gdf)):
        # Get ENACT-POP rasters that touches the current shape
        enact_shape_out_img, enact_shape_out_transform = mask(night_enact, [gdf.iloc[i].geometry], crop=True,
                                                              nodata=-128,
                                                              all_touched=True)
        zone_sum = 0
        zone_poly = Polygon(gdf.iloc[i].geometry)
        for enact_square_geometry, enact_value in features.shapes(enact_shape_out_img.astype(np.float32),
                                                                  transform=enact_shape_out_transform):
            corine_enact_out_img, corine_enact_out_transform = mask(corine, [enact_square_geometry], crop=True,
                                                                    nodata=0,
                                                                    all_touched=True)
            enact_square_poly = Polygon(enact_square_geometry['coordinates'][0])
            enact_area_w_corine = 0
            shape_area_w_corine = 0
            for corine_square_geometry, corine_type in features.shapes(corine_enact_out_img.astype(np.float32),
                                                                       transform=corine_enact_out_transform):
                if corine_type == 0:
                    continue
                corine_square_poly = Polygon(corine_square_geometry['coordinates'][0])
                corine_value = corine_dict[int(corine_type)]
                # Intersections
                corine_enact_overlapping_poly = enact_square_poly.buffer(0).intersection(corine_square_poly.buffer(0))
                corine_enact_shape_overlapping_poly = corine_enact_overlapping_poly.intersection(gdf.iloc[i].geometry)
                if debug_plot:
                    plot_shape_enact_corine_raster(zone_poly, enact_square_poly, corine_square_poly,
                                                   corine_enact_overlapping_poly,
                                                   corine_enact_shape_overlapping_poly)  # Plotting for debugging
                if not corine_enact_overlapping_poly.is_empty:
                    enact_area_w_corine += corine_enact_overlapping_poly.area * corine_value
                if not corine_enact_shape_overlapping_poly.is_empty:
                    shape_area_w_corine += corine_enact_shape_overlapping_poly.area * corine_value
            if enact_area_w_corine > 0:
                zone_sum += shape_area_w_corine / enact_area_w_corine * enact_value
        results.append(zone_sum)
    gdf[prefix + title + "_sum"] = results
    gdf[prefix + title + "_ratio"] = gdf[prefix + title + "_sum"] / gdf[prefix + title + "_sum"].sum()
    return gdf


def upscale_raster(file_path: str, upscale_factor: int = 2, resampling=Resampling.nearest, generate_file: bool = True):
    """
    Upscaling a Raster File.

    Parameters
    ----------
    file_path: str
        File path of the raster to upscale.
    upscale_factor: int (optional)
        Upscale Factor. Default = 2.
    resampling: Resampling
        Resampling Method to use.
    generate_file: bool (default True)
        If True it will generate a new file, If False no.

    Returns
    -------
    data:
        Raster Data
    dataset:
        Raster Dataset
    transform:
        Image Transformation
    profile:
        Dataset profile
    """
    with rasterio.open(file_path) as dataset:
        # resample data to target shape
        data = dataset.read(
            out_shape=(
                dataset.count,
                int(dataset.height * upscale_factor),
                int(dataset.width * upscale_factor)
            ),
            resampling=resampling
        )

        # scale image transform
        transform = dataset.transform * dataset.transform.scale(
            (dataset.width / data.shape[-1]),
            (dataset.height / data.shape[-2])
        )
        profile = dataset.profile
        profile.update(transform=transform, driver='GTiff', height=int(dataset.height * upscale_factor),
                       width=int(dataset.width * upscale_factor), crs=dataset.crs, nodata=data.min())
    if generate_file:
        with rasterio.open(f'output_up_{upscale_factor}.tif', 'w+', **profile) as dst:
            dst.write(data)

    return data, dataset, transform, profile


if __name__ == '__main__':
    root_folder_enact = "./ENACT_POP_2011_EU28_R2019A_3035_1K_V1_0_LF6POPCLASS/"
    for file in os.listdir(root_folder_enact):
        x = root_folder_enact + file
        raster_to_4326(x)
    # generate_day_night_average_november_march_targeted()
