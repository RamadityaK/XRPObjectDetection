import cv2
from picamera2 import Picamera2, Preview
picam2 = Picamera2()
picam2.preview_configuration.main.size=(254,254)
camera_config = picam2.create_still_configuration({"size": (600,600)})
picam2.configure(camera_config)
#picam2.start_preview(Preview.QTGL)
picam2.start()

i = 0
while True:
    im = picam2.capture_array()
    #im = cv2.rotate(im,cv2.ROTATE_90_CLOCKWISE)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    cv2.imshow('preview', im)
    pressedKey = cv2.waitKey(30) & 0xFF
    if pressedKey == ord('p'):
        file = "/home/rama/Desktop/pictures/rbpic"+str(i)+".jpg"
        print('Taking picture: ', file)
        cv2.imwrite(file, im)
        i = i+1
    if pressedKey == ord('q'):
        break
    
picam2.stop()
cv2.destroyAllWindows()


