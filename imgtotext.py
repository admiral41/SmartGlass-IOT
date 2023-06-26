import cv2
import pytesseract
import subprocess

# Initialize the camera
camera = cv2.VideoCapture(0)  # Use the default camera (change the index if necessary)

while True:
    ret, frame = camera.read()

    # Perform OCR on the captured image
    text = pytesseract.image_to_string(frame)
    
    if text:
        # Convert the extracted text to speech using espeak
        subprocess.call(["espeak", text])
    
    cv2.imshow("frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
