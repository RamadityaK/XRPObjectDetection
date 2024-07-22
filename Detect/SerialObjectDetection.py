# Import Mediapipe
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Required Peripheral Libraries
import cv2
import numpy as np
import time

# Initialize the camera object
from picamera2 import Picamera2
picam2 = Picamera2()
picam2.start()

# Initialize the Serial Object
import serial
ser = serial.Serial(
    port='/dev/ttyS0', # Change this based on connection methods
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
    )

base_options = python.BaseOptions(model_asset_path = 'efficientdet.tflite')
options = vision.ObjectDetectorOptions(base_options=base_options,
                                       score_threshold=0.4)
detector = vision.ObjectDetector.create_from_options(options)

#Set Variables
last_time = 0
inference_time = 0
target = 'person'


while True:
    #Grab an image and format it
    image = picam2.capture_array()
    image = cv2.rotate(image, cv2.ROTATE_180) #Change or omit this based on your camera orientation
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #Converts image from BGR to RGB format
    #rgb_image = cv2.resize(rgb_image,(640,640))
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image) #Reformat to Mediapipe format

    #Run inferencing and time it for benchmarking
    last_time = time.time()
    detection_result = detector.detect(mp_image)
    inference_time = time.time() - last_time

    #Initialize Loop Variables
    centroidx = 0
    centroidy = 0
    deviationx = 0
    deviationy = 0
    width = 0
    height = 0
    detected = 0

    #Parse through detections
    for detection in detection_result.detections:
        category = detection.categories[0]
        classification = category.category_name
        #Only execute if the target class matches the detected class
        if(classification == target):
            print(str(round(category.score,2)))
            bbox = detection.bounding_box
            detected = 1
            # Grab Relevant Variables
            width = bbox.width
            height = bbox.height
            centroidx = bbox.origin_x + (width/2)
            centroidy = bbox.origin_y + (height/2)
            deviationx = centroidx - 240
            deviationy = centroidy - 320

            #Print to console for Debugging
            #print(category.category_name, ", with prob: ", str(round(category.score,2)), "and centroid: ", str(centroidx),",",str(centroidy))
            #print('deviation from center: ', str(deviationx), ",", str(deviationy))
    
    #Write our output over the serial port
    output = str(detected) + ',' + str(deviationx) + ',' + str(deviationy) + ',' + str(width) + ',' +str(height)
    ser.write(output.encode())

    #The written data should be of the following format:
    # detected?(1 or 0), xdeviation, ydeviation, box width, box height.
    print(output)
    #print("Inference Time: ", str(time.time()-last_time))
