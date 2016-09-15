import RPi.GPIO as GPIO
include time

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
#setup GPIO using Board numbering
#GPIO.setmode(GPIO.BOARD)


GPIO.setup(18, GPIO.OUT) 
for a in range(10):
	print "high"
	GPIO.output(18, GPIO.HIGH)  #3.3v
	time.sleep(2)
	print "low"
	GPIO.output(18, GPIO.LOW)  #0v
	time.sleep(2)

GPIO.cleanup()