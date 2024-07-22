from XRPLib.defaults import *


from machine import Pin
from time import sleep
import time

#initialize the UART Connection
uart = machine.UART(1, 115200, tx = Pin(8), rx = Pin(9))
#print(uart)

#b = None
msg = ""

#PID Controller Varibles
baseSpeed = 0.18
fwdSpeed = baseSpeed
totalError = 0
Kp = 0.14
Ki = 0.00001
Kd = 0.00001
MaxIntegralContribution = 0.15
saturationThreshold = MaxIntegralContribution/Ki
lastError = 0
speedClamp = 0.3

while True:
    
    #If we get a UART Transmission
    if uart.any():
        #Wait for the full transmission to come in
        time.sleep(.1)
        #Read in the UART Transmission
        b = uart.readline()
        if b:
            # Decode bytes to string
            msg = b.decode().strip()  # Convert bytes to string and strip any extra whitespace
            readings = msg.split(',') # Split the string into a list of strings
            area = 0
            
            # We only want the controller values to update if the transmissin we've gotten is a valid one
            if(int(readings[0])): # If we've gotten a valid update of the target class
                devx = float(readings[1]) #Grab the x deviation from center
                correction = (devx/240) # Scale down the values to -1 to 1
                area = float(readings[3])*float(readings[4]) #Grab the area of the bounding box (rough indication of distance)
                
                #Simple 2 term average filter
                correction = (correction + lastError)/2
                
                #Calculate I Term
                totalError += correction
                if(totalError > saturationThreshold):
                    totalError = saturationThreshold
                
                # Calculate D term
                deltaError = correction - lastError
                lastError = correction
                changeSpeed = (correction*Kp)+(totalError*Ki)+(deltaError * Kd)
                
            else:   # If we get an invalid update
                correction = 0  #Nullify the modification
                changeSpeed = 0
                
            # Clamp the Maximum change in speed
            if(changeSpeed > speedClamp ):
                changeSpeed = speedClamp
            
            if(area>70000):
                fwdSpeed = 0
            else:
                fwdSpeed = baseSpeed
            #Calculate the power to be sent to each motor
            leftmotor = fwdSpeed + changeSpeed
            rightmotor = fwdSpeed - changeSpeed
            
            #Debugging Ouput to USB Console
            print(str(leftmotor), ',',str(rightmotor), ',' ,str(area))
            

            #Assign the motor values to the motors
            drivetrain.set_effort(leftmotor, rightmotor)