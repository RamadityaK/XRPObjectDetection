#Import XRP Library
from XRPLib.defaults import *

#Import Other Libraries
from machine import Pin
from time import sleep
import time

#initialize the UART Connection and a string to hold messages
uart = machine.UART(1, 115200, tx = Pin(8), rx = Pin(9))
msg = ""

#Variables
baseSpeed = 0.19
fwdSpeed = baseSpeed
totalError = 0
endLoop = False
numTriggers = 0

#PID Controller Varibles (You may have to retune the PID for your siutation)
Kp = 0.13
Ki = 0.00001
Kd = 0.03
MaxIntegralContribution = 0.15
saturationThreshold = MaxIntegralContribution/Ki
lastError = 0
speedClamp = 0.15

# Function for XRP Servo1 to lift the basket
def lift_servo(degrees: float = 10):
    drivetrain.set_effort(0,0)
    servo_one.set_angle(degrees)


while True:
    #Reset all variables for next running of the code
    endLoop = False
    fwdSpeed = baseSpeed
    totalError = 0
    lastError = 0
    numTriggers = 0
    board.wait_for_button()    
    lift_servo(20)
    time.sleep(1)
    uart.read() #This line flushes any stale readings in the UART buffer

    while True:
            #If we get a UART Transmission
        if(endLoop): #Break out of this running of the code if we've picked up the basket.
            break
        if uart.any():
            #Wait for the full transmission to come in
            time.sleep(.01)
            #Read in the UART Transmission
            b = uart.readline()
            if b:
                # Decode bytes to string
                msg = b.decode().strip()  # Convert bytes to string and strip any extra whitespace
                readings = msg.split(',') # Split the string into a list of strings
                print(readings)
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
                    fwdSpeed = baseSpeed
                else:   # If we get an invalid update
                    correction = 0  #Nullify the modification
                    changeSpeed = 0
                    fwdSpeed = 0
                    
                # Clamp the Maximum change in speed (Shouldn't be necessary but included anyways)
                if(changeSpeed > speedClamp ):
                    changeSpeed = speedClamp
                if(area >40000):
                    numTriggers = numTriggers + 1
                else:
                    numTriggers = 0
                if(numTriggers>2):
                    
                    fwdSpeed = 0
                    time.sleep(1)
                    drivetrain.turn(20,0.2)
                    time.sleep(1)
                    drivetrain.straight(5, 0.3)
                    time.sleep(1)  
                    lift_servo(70)
                    time.sleep(1)
                    endLoop = True
                    drivetrain.set_effort(0,0)
                    uart.read()
                    
    
                else:
                    fwdSpeed = baseSpeed
                #Calculate the power to be sent to each motor
                leftmotor = fwdSpeed + changeSpeed
                rightmotor = fwdSpeed - changeSpeed
                
                #Debugging Ouput to USB Console
                print(str(leftmotor), ',',str(rightmotor), ',' ,str(area))
                
    
                #Assign the motor values to the motors
                drivetrain.set_effort(leftmotor, rightmotor)
