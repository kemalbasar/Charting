from PIL import Image

# Load the image
image_path = r'F:\pycarhm projects\Charting\valfapp\assets\pers.png'
image = Image.open(image_path)

# Convert the image to RGBA (if not already in this mode)
image = image.convert("RGBA")

# Get data of the image
data = image.getdata()

# List to hold new image data
new_data = []

# Threshold for transparency (how close to white or transparent color)
# You may need to adjust the threshold if the background is not pure white or varies
threshold = 200

# Tuple for the color we wish to replace it with (in this case, transparent)
replace_color = (255, 255, 255, 0)

for item in data:
    # If the color is close to white, make it fully transparent
    # We check if the color is close to white by checking if the R, G, and B values are all above the threshold
    if item[0] > threshold and item[1] > threshold and item[2] > threshold:
        new_data.append(replace_color)
    else:
        new_data.append(item)

# Update image data with new data
image.putdata(new_data)

# Save the new image
output_path = r'F:\pycarhm projects\Charting\valfapp\assets\transparent_background_image.png'
image.save(output_path)

