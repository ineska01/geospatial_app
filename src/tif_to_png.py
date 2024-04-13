from PIL import Image
import os


def convert_tif_to_png(input_folder, output_folder):
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


if __name__ == "__main__":
    input_folder = r"C:\Users\Ineska\Desktop\frontend\src\input_folder"
    output_folder = r"C:\Users\Ineska\Desktop\frontend\src\output_folder"

    convert_tif_to_png(input_folder, output_folder)
