from PIL import Image
import os

# specify your path
path = "/Users/nmekonnen/Downloads/Aws homeheart images copy 2"

for filename in os.listdir(path):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img = Image.open(os.path.join(path, filename))
        width, height = img.size   # Get dimensions

        # Define desired width and height
        desired_width = 600
        desired_height = 400

        # If the image is wider than it is tall
        if width > height:
            new_width = desired_width
            new_height = int(new_width * height / width)
        else:
            new_height = desired_height
            new_width = int(new_height * width / height)

        # Resize the image
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Save the resized image
        img.save(os.path.join(path, filename))
