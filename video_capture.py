import cv2

SECONDS_TO_SKIP = 5

# TODO print to log
class VideoCapture():

    # Variables to store the coordinates of the selected ROI
    roi_selected = False
    roi_start = (0, 0)
    roi_end = (0, 0)
    cap = None
    current_frame = 0
    total_frames = None
    fps = None

    def __init__(self, path, roi_start=None, roi_end=None):
        self.path = path

        if not roi_start or not roi_end:
            self.roi_selected = False
            self._save_crop_factor()
        else:
            self.roi_start, self.roi_end, self.roi_selected = roi_start, roi_end, True

    def _save_crop_factor(self):
        # Mouse callback function
        def select_roi(event, x, y, flags, param):

            if event == cv2.EVENT_LBUTTONDOWN:
                self.roi_start = (x, y)
                self.roi_selected = False

            elif event == cv2.EVENT_LBUTTONUP:
                self.roi_end = (x, y)
                self.roi_selected = True

        # Open the video file
        cap = cv2.VideoCapture(self.path)

        # Check if the file is opened successfully
        if not cap.isOpened():
            print("Error opening video file")
            exit()

        # Read the first frame
        _, image = cap.read()

        # Create a window and set the mouse callback function
        cv2.namedWindow('Select ROI')
        cv2.setMouseCallback('Select ROI', select_roi)

        while True:
            img_display = image.copy()

            # Draw rectangle while selecting
            if self.roi_selected:
                cv2.rectangle(img_display, self.roi_start, self.roi_end, (0, 255, 0), 2)

            cv2.imshow('Select ROI', img_display)
            key = cv2.waitKey(1) & 0xFF

            # Exit on 'esc' key press
            if key == 27:
                break

            # Press 'c' to confirm and store the ROI coordinates
            elif key == ord('c'):
                # Ensure correct coordinates order for the region of interest
                x1, y1 = min(self.roi_start[0], self.roi_end[0]), min(self.roi_start[1], self.roi_end[1])
                x2, y2 = max(self.roi_start[0], self.roi_end[0]), max(self.roi_start[1], self.roi_end[1])
                selected_image = image[y1:y2, x1:x2]

                # You can further process or save the selected_roi here
                cv2.imshow('Selected ROI', selected_image)
                cv2.waitKey(0)  # Wait for any key press before closing the ROI window
                cv2.destroyWindow('Selected ROI')
                break

        # Release resources and close windows
        cap.release()
        cv2.destroyAllWindows()

    def read_frame_local(self, seconds_to_skip=SECONDS_TO_SKIP):
        if not self.cap:
            self.cap = cv2.VideoCapture('rec_2023-12-17_18-02.mp4')
            if not self.cap.isOpened():
                print("Error opening video file")
                exit()

            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        if self.current_frame < self.total_frames:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.cap.read()
            if ret:
                self.current_frame += self.fps * seconds_to_skip
                x1, y1 = min(self.roi_start[0], self.roi_end[0]), min(self.roi_start[1], self.roi_end[1])
                x2, y2 = max(self.roi_start[0], self.roi_end[0]), max(self.roi_start[1], self.roi_end[1])
                return frame[y1:y2, x1:x2]
            else:
                self.cap.release()
                return None
        else:
            self.cap.release()
            return None

    

if __name__ == "__main__":
    vc = VideoCapture(path='rec_2023-12-17_18-02.mp4')
    print(vc.roi_start)
    print(vc.roi_end)
