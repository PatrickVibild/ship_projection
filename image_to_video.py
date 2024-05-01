import cv2
import os
import re
from glob import glob

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

def make_video(image_folder, video_name, fps=10):
    # Get all image paths
    images = glob(os.path.join(image_folder, '*.jpg'))
    images.sort(key=natural_sort_key)  # Sort the images by name naturally

    # Determine the width and height from the first image
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
    out = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    for image in images:
        frame = cv2.imread(image)
        out.write(frame)  # Write out frame to video

    out.release()  # Release the video writer


if __name__ == '__main__':
    make_video('/home/patrick/dataset_no_focus/1698207737/rgb', '1698207737.mp4')
# This function would be called with the path to the image folder and the desired video file name:
# make_video('path_to_images', 'output_video.mp4', 10)
