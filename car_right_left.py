import RPi.GPIO as GPIO
import time
Motor_Pin1 = 16
Motor_Pin2 = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Motor_Pin1, GPIO.OUT)
GPIO.setup(Motor_Pin2, GPIO.OUT)
try:
    GPIO.output(Motor_Pin1, True) # clockwise
    time.sleep(3)
    GPIO.output(Motor_Pin1, False)
    time.sleep(1) # protect motor
    GPIO.output(Motor_Pin2, True) # counterclockwise
    time.sleep(3)
    GPIO.output(Motor_Pin2, False)
finally:
    GPIO.cleanup()
