from PIL import Image
import piexif
import os

#Do not change this. this shit finally works. I almost lost my sanity but it works! Yippeeeee

def compress_images(output_folder, update_progress):
    # Define the input folder (sorted images location stuffs)
    input_image_folder = os.path.join(output_folder, 'temp', 'images')

    # Check if there are any images to compress
    if not os.path.exists(input_image_folder) or not os.listdir(input_image_folder):
        update_progress("No images to compress. Skipping step.", 100)  # Report 100% progress cuz yk nothing to do
        return  # Exit the function early

    # Create the output folder if it doesn't exist
    output_image_folder = os.path.join(output_folder, 'Images')
    os.makedirs(output_image_folder, exist_ok=True)

    # Get the list of image files in the input folder
    image_files = [os.path.join(input_image_folder, f) for f in os.listdir(input_image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif', '.svg'))]

    # Compress each image
    for i, image_file in enumerate(image_files):
        try:
            # Open the image
            img = Image.open(image_file)

            # Extract metadata (EXIF) from the original image (I hate bugs about exif. may the gods save me from having to play with this again)
            exif_dict = None
            if 'exif' in img.info:
                try:
                    exif_dict = piexif.load(img.info['exif'])
                except Exception as e:
                    update_progress(f"Error loading EXIF metadata from {os.path.basename(image_file)}: {str(e)}")

            # Save the image in WebP format with metadata (if available (and if not do not crash the whole god damn piece of shit))
            output_path = os.path.join(output_image_folder, os.path.basename(image_file).split('.')[0] + '.webp')
            if exif_dict:
                img.save(output_path, 'WEBP', quality=80, exif=piexif.dump(exif_dict))
            else:
                img.save(output_path, 'WEBP', quality=80)

            update_progress(f"Compressed {os.path.basename(image_file)}", (i + 1) / len(image_files) * 100)
        except Exception as e:
            update_progress(f"Error compressing {image_file}: {str(e)}")