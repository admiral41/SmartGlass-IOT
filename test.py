import cv2
import time
from espeak import espeak
import RPi.GPIO as GPIO

# Ultrasonic sensor pin configuration
TRIG = 27
ECHO = 22

# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Distance calculation function using ultrasonic sensor
def read_distance():
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    pulse_start = time.time()
    while GPIO.input(ECHO) != GPIO.HIGH:
        pulse_start = time.time()

    pulse_end = pulse_start
    while time.time() < pulse_start + 0.1:
        if GPIO.input(ECHO) == GPIO.LOW:
            pulse_end = time.time()
            break

    pulse_duration = pulse_end - pulse_start
    distance = 34300 * pulse_duration / 2

    if distance <= 400:
        return distance
    else:
        return None

# Speech synthesis function using espeak
def speak(text):
    espeak.synth(text)

classNames = []
classFile = "coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box, className])
                if draw:
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                    distance = read_distance()
                    if distance is not None and distance <= 18:
                        speak(f"Obstacle is a {className} at a distance of {distance} centimeters")

    return img, objectInfo


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        success, img = cap.read()
        result, objectInfo = getObjects(img, 0.55, 0.2, objects=['cup', 'person', 'car', 'keyboard', 'mouse', 'laptop'])
        cv2.imshow("Output", img)
        cv2.waitKey(1)

    GPIO.cleanup()
