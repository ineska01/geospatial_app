from PIL import Image, ImageDraw
import os
import io
from glob import glob
from ultralytics import YOLO
import shutil
import rasterio
import json


def tif_to_png_with_save(input_folder, output_folder):
    my_list = os.listdir(input_folder)
    for filename in my_list:
        if filename.endswith(".tif"):
            tif_path = os.path.join(input_folder, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(output_folder, png_filename)

            try:
                img = Image.open(tif_path)
                img.save(png_path, "PNG")
                print(f"Konwertowano: {tif_path} -> {png_path}")
            except Exception as e:
                print(f"Błąd podczas konwersji {tif_path}: {str(e)}")


def tif_to_png_without_save(tif_data):
    tif_image = Image.open(io.BytesIO(tif_data))
    with io.BytesIO() as output:
        tif_image.save(output, format="PNG")
        png_data = output.getvalue()
    return png_data


def change_resolution_fullhd(input_directory, output_directory):
    input_directory = r"C:\Users\user\Desktop\frontend\output_folder"

    new_width = 1920
    new_height = 1080

    output_directory = r"C:\Users\user\Desktop\frontend\resolution_fullhd"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    my_list = os.listdir(input_directory)
    for filename in my_list:
        if filename.endswith(".png"):
            input_path = os.path.join(input_directory, filename)
            image = Image.open(input_path)

            left = (image.width - new_width) / 2
            top = (image.height - new_height) / 2
            right = (image.width + new_width) / 2
            bottom = (image.height + new_height) / 2

            cropped_image = image.crop((left, top, right, bottom))
            output_path = os.path.join(output_directory, filename)

    cropped_image.save(output_path)
    cropped_image.close()


def save_png_to_local_folder(png_data, folder_path, original_file_name):
    base_name = os.path.splitext(original_file_name)[0]
    file_name = f"res.png"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "wb") as f:
        f.write(png_data)

    return file_path


def detect_objects(image_path, model):
    detection_results = model.predict(image_path, save=True, conf=0.5, save_txt=True)
    return detection_results


def draw_bounding_boxes(image, bounding_boxes):
    draw = ImageDraw.Draw(image)
    for box in bounding_boxes:
        draw.rectangle(box, outline="red", width=2)
    return image


def find_detection_results(image_path, output_folder):
    image_name = os.path.basename(image_path)
    result_pattern = os.path.join(
        output_folder, "predictions", image_name.replace(".png", "") + "*"
    )
    result_files = glob(result_pattern)
    return result_files


def get_infered_pic():
    return r"runs\segment\predict\res.png"


def detect_to_geojson(raster_path: str, labels_txt: str, save_dir: str):
    with rasterio.open(raster_path) as src:
        bounds = src.bounds

    top = bounds[3]
    bottom = bounds[1]
    right = bounds[2]
    left = bounds[0]
    total_width = abs(left - right)
    total_height = abs(top - bottom)

    boiler_plate = {
        "type": "FeatureCollection",
        "name": "finall_merged",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::2180"}},
        "features": [],
    }

    bullet = {
        "type": "Feature",
        "properties": {"id": "null"},
        "geometry": {"type": "MultiPolygon", "coordinates": [[]]},
    }

    with open(labels_txt) as f:
        lines = f.readlines()

    for line in lines:
        line_parts = line.split()
        points_list = []
        temp_list = []
        re_list = line_parts[1:]
        for index, part in enumerate(re_list):
            is_pa = index % 2

            if is_pa == 0:
                counted_value_wy = float(part) * total_width
                point_value_y = left + counted_value_wy
                temp_list.append(point_value_y)

            if is_pa != 0:
                counted_value_sze = float(part) * total_height
                point_value_x = top - counted_value_sze
                temp_list.append(point_value_x)
                points_list.append(temp_list)
                temp_list = []

        bullet["geometry"]["coordinates"][0].append(points_list)

    boiler_plate["features"].append(bullet)

    with open(save_dir, "w") as f:
        json.dump(boiler_plate, f)


def clear_after_user():
    shutil.rmtree("runs")
    shutil.rmtree("data")
    os.makedirs("data")


if __name__ == "__main__":
    input_folder = r"C:\Users\user\Desktop\frontend\input_folder"
    output_folder = r"C:\Users\user\Desktop\frontend\output_folder"

    tif_to_png_with_save(input_folder, output_folder)
    detect_to_geojson(
        "data/ort_23.tif",
        "data/res1.txt",
        "data/list_of_poligons/finall_merged.geojson",
    )
