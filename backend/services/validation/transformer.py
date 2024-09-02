from PIL import Image
import io


def resize_png(image, max_size):
    try:
        # Open the image and resize it
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height
        new_width = int((max_size * aspect_ratio) ** 0.5)
        new_height = int(new_width / aspect_ratio)

        # TODO check for necessary calling of resize
        image = image.resize((new_width, new_height))
        
        while True:
            # Save the image to a BytesIO object
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')

            # Check the size of the image
            if image_bytes.tell() < max_size:
                break

            # If the image is too large, reduce its dimensions
            width, height = image.size
            image = image.resize((width - 15, height - 15))

        # Update the position of the file to the beginning after streaming
        image_bytes.seek(0)

        return image_bytes
    
    except Exception as error:
        print(f"An error occurred: {error}")
