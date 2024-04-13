from PIL import Image
import os

input_directory = r"C:\Users\Ineska\Desktop\frontend\src\output_folder"

new_width = 1920
new_height = 1080

output_directory = r"C:\Users\Ineska\Desktop\frontend\src\resolution_fullhd"

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
