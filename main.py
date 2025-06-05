import RPi.GPIO as GPIO
import time
import random

GPIO.setmode(GPIO.BCM)

LEFT_FORWARD = 21
LEFT_BACKWARD = 20
RIGHT_FORWARD = 23
RIGHT_BACKWARD = 24

BUTTON_PIN = 26
LIGHT_SENSOR_PIN = 6
LED_PIN = 16

motor_pins = [LEFT_FORWARD, LEFT_BACKWARD, RIGHT_FORWARD, RIGHT_BACKWARD]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIGHT_SENSOR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.HIGH)  # LED always ON

def rc_time(pin):
    count = 0
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.01)
    GPIO.setup(pin, GPIO.IN)

    while GPIO.input(pin) == GPIO.LOW:
        count += 1
        if count > 10000:
            break
    return count

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

def turn_right():
    GPIO.output(LEFT_FORWARD, GPIO.HIGH)
    GPIO.output(LEFT_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_FORWARD, GPIO.LOW)
    GPIO.output(RIGHT_BACKWARD, GPIO.HIGH)

def main():
    motor_running = False
    last_button_state = GPIO.input(BUTTON_PIN)

    state = "IDLE"
    state_start_time = 0
    turn_direction = None

    try:
        while True:
            current_button_state = GPIO.input(BUTTON_PIN)
            if last_button_state == GPIO.HIGH and current_button_state == GPIO.LOW:
                motor_running = not motor_running
                if motor_running:
                    print("Button pressed: Starting in 5 seconds")
                    stop()
                    time.sleep(5)
                    state = "TURNING"
                    turn_direction = random.choice([turn_left, turn_right])
                    state_start_time = time.time()
                else:
                    print("Button pressed: Stopping robot")
                    stop()
                    state = "IDLE"

            last_button_state = current_button_state

            if motor_running:
                light_level = rc_time(LIGHT_SENSOR_PIN)
                current_time = time.time()
                elapsed = current_time - state_start_time

                if state == "TURNING":
                    turn_direction()
                    if elapsed > 0.7:
                        state = "FORWARD"
                        state_start_time = current_time

                elif state == "FORWARD":
                    if light_level < 300:
                        forward()
                        if elapsed > 3:
                            state = "TURNING"
                            turn_direction = random.choice([turn_left, turn_right])
                            state_start_time = current_time
                    else:
                        state = "BACKWARD"
                        state_start_time = current_time
                        stop()

                elif state == "BACKWARD":
                    backward()
                    if elapsed > 1:
                        state = "TURNING"
                        turn_direction = random.choice([turn_left, turn_right])
                        state_start_time = current_time

                else:
                    stop()

            else:
                stop()
                state = "IDLE"

            time.sleep(0.05)

    except KeyboardInterrupt:
        stop()
        GPIO.cleanup()
        print("Program terminated.")

if __name__ == "__main__":
    main()
