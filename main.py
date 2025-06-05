import RPi.GPIO as GPIO
import time
import random

GPIO.setmode(GPIO.BCM)

# Motor pins (adjust to your wiring)
LEFT_FORWARD = 21
LEFT_BACKWARD = 20
RIGHT_FORWARD = 23
RIGHT_BACKWARD = 24

# Button and light sensor pins
BUTTON_PIN = 26
LIGHT_SENSOR_PIN = 6
LED_PIN = 16

# Setup pins
motor_pins = [LEFT_FORWARD, LEFT_BACKWARD, RIGHT_FORWARD, RIGHT_BACKWARD]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button with pull-up resistor
GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

# RC timing function for light sensor reading (lower = white, higher = black)
def rc_time(pin):
    count = 0
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(pin, GPIO.IN)

    while GPIO.input(pin) == GPIO.LOW:
        count += 1
        if count > 10000:  # safety to prevent infinite loop
            break
    return count

# Motor control functions
def stop():
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)

def forward():
    GPIO.output(LEFT_FORWARD, GPIO.HIGH)
    GPIO.output(LEFT_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_FORWARD, GPIO.HIGH)
    GPIO.output(RIGHT_BACKWARD, GPIO.LOW)

def backward():
    GPIO.output(LEFT_FORWARD, GPIO.LOW)
    GPIO.output(LEFT_BACKWARD, GPIO.HIGH)
    GPIO.output(RIGHT_FORWARD, GPIO.LOW)
    GPIO.output(RIGHT_BACKWARD, GPIO.HIGH)

def turn_left():
    GPIO.output(LEFT_FORWARD, GPIO.LOW)
    GPIO.output(LEFT_BACKWARD, GPIO.HIGH)
    GPIO.output(RIGHT_FORWARD, GPIO.HIGH)
    GPIO.output(RIGHT_BACKWARD, GPIO.LOW)
    time.sleep(2) #turns for 2 seconds

def turn_right():
    GPIO.output(LEFT_FORWARD, GPIO.HIGH)
    GPIO.output(LEFT_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_FORWARD, GPIO.LOW)
    GPIO.output(RIGHT_BACKWARD, GPIO.HIGH)
    time.sleep(2) #turns for 2 seconds

# Main functions
def Go():
    # Choose random turn direction before moving forward
    turn_func = random.choice([turn_left, turn_right])
    print("Go(): Turning first")
    turn_func()
    time.sleep(0.5)  

    print("Go(): Moving forward")
    forward()
    time.sleep(5)  # move forward for 5 seconds

def Stop():
    print("Stop(): Edge detected! Stopping and reversing")
    stop()
    time.sleep(0.2)
    backward()
    time.sleep(1)  # reverse for 1 second

    # Turn away from edge
    turn_func = random.choice([turn_left, turn_right])
    print("Stop(): Turning away from edge")
    turn_func()
    time.sleep(0.5)

    stop()

# Main program
def main():
    motor_running = False
    last_button_state = GPIO.input(BUTTON_PIN)
    
    try:
        while True:
            GPIO.output(LED_PIN, GPIO.HIGH)

            current_button_state = GPIO.input(BUTTON_PIN)
            # Detect button press (falling edge)
            if last_button_state == GPIO.HIGH and current_button_state == GPIO.LOW:
                motor_running = not motor_running
                if motor_running:
                    print("Button pressed: Starting in 5 seconds")
                    stop()
                    time.sleep(5)  # initial delay
                else:
                    print("Button pressed: Stopping robot")
                    stop()

            last_button_state = current_button_state

            if motor_running:
                light_level = rc_time(LIGHT_SENSOR_PIN)
                print(f"Light sensor value: {light_level}")

                # Threshold depends on your sensor calibration; here 300 as example
                if light_level < 300:
                    # On white (safe zone)
                    Go()
                else:
                    # On black (edge)
                    Stop()
            else:
                stop()

            time.sleep(0.1)  # small delay to reduce CPU usage

    except KeyboardInterrupt:
        stop()
        GPIO.cleanup()
      

if __name__ == "__main__":
    main()
