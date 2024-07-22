# Import Required Libraries
import cv2
from picamera2 import Picamera2, Preview

#Initialize the Raspberry Pi Camera
picam2 = Picamera2()
picam2.preview_configuration.main.size=(254,254) #Set the size of the preview window
camera_config = picam2.create_still_configuration({"size": (600,600)}) #Set the size of the camera's output
picam2.configure(camera_config) #Pass in the configuration
picam2.start() #Start the camera

#Initialize a variable to keep track of the number of pictures we're taking
i = 0
#Initialize a variable to set the directory (YOU MUST SET THIS VARIABLE TO YOUR OWN PICTURE DIRECTORY)
directory = "/home/pi/Desktop/pictures/rbpic"

while True:
    #Capture a picture from the camera
    im = picam2.capture_array()
    #im = cv2.rotate(im,cv2.ROTATE_90_CLOCKWISE) #Optional rotation of the picture
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB) #Convert the picture from BGR to RGB format
    cv2.imshow('preview', im)   #Display a preview of the picture
    pressedKey = cv2.waitKey(30) & 0xFF #Wait for a key to be pressed and take only the last byte
    if pressedKey == ord('p'): #If you press p on the keyboard
        file = directory+str(i)+".jpg" #Create a unique filename
        print('Taking picture: ', file) 
        cv2.imwrite(file, im) #Write the file to the folder
        i = i+1
    if pressedKey == ord('q'): #Quit if q is pressed
        break

#Clean up
picam2.stop()
cv2.destroyAllWindows()


