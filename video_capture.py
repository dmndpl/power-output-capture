import cv2

class VideoCapture():

    # Variables to store the coordinates of the selected ROI
    roi_selected = False
    roi_start = (0, 0)
    roi_end = (0, 0)

    def __init__(self, path, is_local=True):
        self.path = path

    def get_crop_preferences(self):
        pass



    def save_roi(self):
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

if __name__ == "__main__":
    vc = VideoCapture(path='rec_2023-12-17_18-02.mp4')
    vc.save_roi()
    print(vc.roi_start)
    print(vc.roi_end)
