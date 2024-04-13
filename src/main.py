import streamlit as st
from PIL import Image, ImageDraw
import os
import time
from glob import glob
from ultralytics import YOLO
import shutil
import rasterio
import json


def save_tif_to_local_folder(tif_data, folder_path, original_file_name):
    base_name = os.path.splitext(original_file_name)[0]
    file_name = f"res.tif"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "wb") as f:
        f.write(tif_data)
        f.seek(0)

    return file_path


def tif_to_png_with_save(data_folder_path, output_folder):
    my_list = os.listdir(data_folder_path)
    for filename in my_list:
        if filename.endswith(".tif"):
            tif_path = os.path.join(data_folder_path, filename)
            png_filename = os.path.splitext(filename)[0] + ".png"
            png_path = os.path.join(output_folder, png_filename)
            try:
                img = Image.open(tif_path)
                img.save(png_path, "PNG")
                print(f"Konwertowano: {tif_path} -> {png_path}")
            except Exception as e:
                print(f"Błąd podczas konwersji {tif_path}: {str(e)}")

    return png_path


def detect_objects(image_path, model, classes_list):
    detection_results = model.predict(
        image_path,
        save=True,
        conf=0.25,
        iou=0.7,
        save_txt=True,
        show_boxes=False,
        classes=classes_list,
    )
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


def display_detection_images(run_folder_path):
    images = glob(os.path.join(run_folder_path, "*.png"))
    for image_path in images:
        st.image(
            Image.open(image_path), caption="Detected Objects", use_column_width=True
        )


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
    shutil.rmtree(r"C:\Users\Ineska\Desktop\frontend\src\data")
    shutil.rmtree(r"C:\Users\Ineska\Desktop\frontend\src\output")
    os.makedirs(r"C:\Users\Ineska\Desktop\frontend\src\data")
    os.makedirs(r"C:\Users\Ineska\Desktop\frontend\src\output")


def main():
    st.write(
        "<h1 style='text-align: center; font-size: 45px;'>Segmentacja obiektów przestrzennych ze zdjęć satelitarnych</h1>",
        unsafe_allow_html=True,
    )
    st.header(" ", divider="rainbow")
    st.markdown(
        "<h1 style='text-align: center; font-size: 25px;'>Wybierz plik TIF i wgraj go poniżej</h1>",
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(" ", type=["tif"])
    st.markdown(
        "<h1 style='text-align: center; font-size: 15px;'>Wybierz klasę do segmentacji</h1>",
        unsafe_allow_html=True,
    )
    classes_list = []
    budynki_checkbox = st.checkbox("Budynki", key=None)
    drogi_checkbox = st.checkbox("Drogi", key=None)
    woda_checkbox = st.checkbox("Woda", key=None)
    if budynki_checkbox:
        classes_list.append(0)
    if drogi_checkbox:
        classes_list.append(1)
    if woda_checkbox:
        classes_list.append(2)
    st.markdown(
        "<h1 style='text-align: center; font-size: 25px;'>Aby przeprowadzić segmentację kliknij w przycisk poniżej</h1>",
        unsafe_allow_html=True,
    )
    if not classes_list:
        st.warning(
            "Wybierz co najmniej jedną klasę przed przeprowadzeniem segmentacji."
        )
    else:
        agree_button = st.button(
            "Segmentacja obiektów",
            args=None,
            kwargs=None,
            disabled=False,
            use_container_width=True,
        )
        if uploaded_file is not None and agree_button:
            if uploaded_file.type == "application/octet-stream":
                st.error("Invalid file format. Please choose a TIF file.")
                return

            data_folder_path = os.path.join(os.path.dirname(__file__), "data")
            tif_data = uploaded_file.read()
            saved_tif_path = save_tif_to_local_folder(
                tif_data, data_folder_path, uploaded_file.name
            )

            os.makedirs(data_folder_path, exist_ok=True)
            os.makedirs(data_folder_path, exist_ok=True)

            progress_text = "Operacja w toku. Proszę zaczekać."
            my_bar = st.progress(0, text=progress_text)
            output_folder = os.path.join(os.path.dirname(__file__), "data")
            saved_path = tif_to_png_with_save(data_folder_path, output_folder)
            png_data = r"C:\Users\Ineska\Desktop\frontend\src\data\res.png"
            st.image(
                Image.open(png_data),
                caption="Wgrana ortofotomapa",
                use_column_width=True,
            )
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(1)
            save = st.markdown(
                "<h1 style='text-align: center; font-size: 20px;'>Zdjęcie satelitarne jest w trakcie segmentacji</h1>",
                unsafe_allow_html=True,
            )
            my_bar.empty()
            time.sleep(6)
            save.empty()

            model = YOLO(r"C:\Users\Ineska\Desktop\frontend\models\best_300_3class.pt")

            detection_results = detect_objects(saved_path, model, classes_list)

            st.image(
                get_infered_pic(),
                caption="Ortofotomapa z etykietami",
                use_column_width=True,
            )

            runs_folder_path = os.path.join(os.path.dirname(__file__), "runs")
            display_detection_images(runs_folder_path)
            raster_path = r"C:\Users\Ineska\Desktop\frontend\src\data\res.tif"
            labels_txt = (
                r"C:\Users\Ineska\Desktop\frontend\runs\segment\predict\labels\res.txt"
            )
            save_dir = r"C:\Users\Ineska\Desktop\frontend\src\output\res.geojson"
            print(save_dir)
            try:
                detect_to_geojson(raster_path, labels_txt, save_dir)
            except:
                st.markdown(
                    "<h1 style='text-align: center; font-size: 25px;'>Nie udało się przeprowadzić segmentacji</h1>",
                    unsafe_allow_html=True,
                )

            file_path = r"C:\Users\Ineska\Desktop\frontend\src\output\res.geojson"
            framed_text_code = """
                    <div style="border: 2px solid #878787; padding: 3px; margin-bottom: 15px;">
                        <h1 style='text-align: center; font-size: 25px;'>Kliknij w przycisk poniżej, aby pobrać zaznaczone obiekty</h1>
                    </div>
                """
            st.markdown(framed_text_code, unsafe_allow_html=True)
            try:
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="Pobierz GeoJSON",
                        data=file,
                        file_name="res.geojson",
                        mime="application/geo+json",
                        args=None,
                        kwargs=None,
                        disabled=False,
                        use_container_width=True,
                    )
            except:
                st.markdown(
                    "<h1 style='text-align: center; font-size: 20px; color: red;'>Brak pliku do pobrania</h1>",
                    unsafe_allow_html=True,
                )

            st.text("")
            st.text("")

            if st.button(
                "Wróć do początku",
                args=None,
                kwargs=None,
                disabled=False,
                use_container_width=True,
                type="primary",
            ):

                st.rerun()

            clear_after_user()


if __name__ == "__main__":
    main()
