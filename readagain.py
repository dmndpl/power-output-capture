import cv2
import requests
import os
from io import BytesIO
from PIL import Image
from google.cloud import vision_v1
from google.cloud.vision_v1 import types

# Replace these with your own values
IP_WEBCAM_URL = os.environ.get("IP_WEBCAM_URL")
API_KEY = os.environ.get("API_KEY")
CREDS_PATH = os.environ.get("CREDS_PATH")

IMAGE_CAPTURE_INTERVAL = 1 # 6 in seconds
NUM_READINGS_PER_BURST = 1 # 10
NUM_BURSTS_PER_HOUR = 1

# Coordinates of the top-left and bottom-right corners of the ROI
ROI_TOP_LEFT = (110,180)
ROI_BOTTOM_RIGHT = (320,280)

SECONDS_TO_SKIP = 5

# Initialize the Google Cloud Vision API client
client = vision_v1.ImageAnnotatorClient.from_service_account_file(CREDS_PATH)

def extract_digits(image, crop=True):
    # Crop the frame to the region of interest
    roi = image[ROI_TOP_LEFT[1]:ROI_BOTTOM_RIGHT[1], ROI_TOP_LEFT[0]:ROI_BOTTOM_RIGHT[0]] if crop else image
     
    # Check if the cropped image has a valid size
    if roi.shape[0] > 0 and roi.shape[1] > 0:
        # Display the cropped image for visual verification
        # cv2.imshow("Cropped Image", roi)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

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

def extract_from_local(extraction):
    # Open the video file
    cap = cv2.VideoCapture('rec_2023-12-17_18-02.mp4')

    # Check if the file is opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        exit()

    fps = cap.get(cv2.CAP_PROP_FPS)

    frames_to_skip = fps * SECONDS_TO_SKIP
    frame_count = 0
    # Read and display frames until the video is over or manually stopped
    while cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
        ret, frame = cap.read()

        # If a frame is read properly, ret will be True
        if ret:
            # Display the frame
            #cv2.imshow('Frame', frame)
            frame_count += frames_to_skip

            # Extract digits from the frame
            digits = extraction(frame, crop=False)

            # Print or store the digits as needed
            print(parse_text(digits[-2:]))

            # Press 'q' to exit the video
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

    # Release the video capture object and close windows
    cap.release()
    cv2.destroyAllWindows()

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
    # TODO there's an edge case where it only sees the Pro, not the whole url, so we end up extracting the PRO instead of the value
    if text[0] == 'https://ipwebo.am/pro':
        return text[1]

    return text[0]
def main():
    #extract_from_local(extract_digits)
    result = stream_to_rows(data_list)
    for row in result:
        print(row)

if __name__ == "__main__":
    main()

