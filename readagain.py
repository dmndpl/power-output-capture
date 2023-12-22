import cv2
import requests
import os
from io import BytesIO
from PIL import Image
from video_capture import VideoCapture
from google.cloud import vision_v1
from google.cloud.vision_v1 import types

# Replace these with your own values
IP_WEBCAM_URL = os.environ.get("IP_WEBCAM_URL")
API_KEY = os.environ.get("API_KEY")
CREDS_PATH = os.environ.get("CREDS_PATH")

# TODO to revisit these
IMAGE_CAPTURE_INTERVAL = 1 # 6 in seconds
NUM_READINGS_PER_BURST = 1 # 10
NUM_BURSTS_PER_HOUR = 1

SECONDS_TO_SKIP = 5

# Initialize the Google Cloud Vision API client
client = vision_v1.ImageAnnotatorClient.from_service_account_file(CREDS_PATH)

def extract_digits(image):
    # Check if the image has a valid size
    if image.shape[0] > 0 and image.shape[1] > 0:
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Perform OCR using Google Cloud Vision API
        _, encoded_image = cv2.imencode('.jpg', gray)
        content = encoded_image.tobytes()

        image = types.Image(content=content)
        response = client.text_detection(image=image)

        # Extract the detected text
        texts = response.text_annotations
        extracted_digits = [text.description for text in texts]

        return extracted_digits
    else:
        print("Invalid size for the cropped image. Check ROI coordinates.")


def extract_from_stream(extraction):
    cap = cv2.VideoCapture(IP_WEBCAM_URL)

    for _ in range(NUM_BURSTS_PER_HOUR):
        for _ in range(NUM_READINGS_PER_BURST):
            # Capture a frame from the video stream
            ret, frame = cap.read()

            # Extract digits from the frame
            digits = extraction(frame)

            # Print or store the digits as needed
            print(digits)

            # Wait for the next capture interval
            cv2.waitKey(IMAGE_CAPTURE_INTERVAL * 1000)

    # Release the video capture object
    cap.release()

data_list = [
    "17/12/2823",
    "1/12/2923",
    "18:21",
    "Pro",
    "096,16",
    "004948",
    "000,64",
    "000,64",
    "001140",
    "002163",
    "210022132",
    "ABR",
    "7/12/2023",
    "1/12/2023",
    "18:22",
    "008080",
    "096,16",
    "004948",
    "000,64",
    "000,64",
    "001140",
    "092163",
    "210022132",
    "ABR",
    "7/12/2023",
    "2/12/2023",
    "18:23",
    "008080",
    "096,16",
    "004948",
    "000,64",
    "000,64",
    "001140",
    "092163",
    "210022132",
    "ABR",
    "7/12/2023",
    "7/12/2023",
    "18:24",
    "008080",
    "096,16",
    "004948",
    "000,64",
    "000,64",
    "001140",
    "092163",
    "210022132",
    "ARR",
    "7/12/2923",
    "27/12/2023",
    "18:25",
    "Pro", 
    "096,16",
    "004948",
    "000,64",
    "000,64",
    "001140",
    "002163",
    "10022132",
    "ABR"
]

def stream_to_rows(stream):
    rows = []
    row = []
    start = False

    LINE_BREAKS = ["ABR", "ARR"]

    # TODO state machine, to sanitise the values and have the correct values at the correct position as we go.
    for item in stream:
        if start and item not in LINE_BREAKS:
            row.append(item)
        elif start and item in LINE_BREAKS:
            rows.append(row)
            row = []
        elif not start and item in LINE_BREAKS:
            start = True
    # We don't care if item is not ABR and start is False

    return rows

def parse_text(text):
    return text
    # TODO there's an edge case where it only sees the Pro, not the whole url, so we end up extracting the PRO instead of the value
    if text[0] == 'https://ipwebo.am/pro':
        return text[1]

    return text[0]

def main():
    vc = VideoCapture(path='rec_2023-12-17_18-02.mp4')

    frame = vc.read_frame_local()
    while frame is not None:
        digits = extract_digits(frame)
        print(digits)
        frame = vc.read_frame_local()


if __name__ == "__main__":
    # TODO Read stream or frames from video, and write result as array somewhere as aprocess
    # TODO Other process reads it and parses it, writes it to another file
    main()
