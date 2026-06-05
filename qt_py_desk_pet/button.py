import time
import board
import digitalio

EVENT_NONE = 0
EVENT_SHORT = 1
EVENT_LONG = 2
EVENT_DOUBLE = 3

class GestureButton:
    def __init__(self, pin=board.BUTTON):
        self.btn = digitalio.DigitalInOut(pin)
        self.btn.direction = digitalio.Direction.INPUT
        self.btn.pull = digitalio.Pull.UP
        
        self.state = False
        self.last_state = False
        self.pressed_time = 0
        self.released_time = 0
        
        self.waiting_for_double = False
        self.double_click_threshold = 0.4
        self.long_press_threshold = 1.0

    def update(self):
        # Read inverted (pull up means False is pressed)
        current_state = not self.btn.value
        now = time.monotonic()
        event = EVENT_NONE
        
        # Transition: Released -> Pressed
        if current_state and not self.last_state:
            self.pressed_time = now
            
        # Transition: Pressed -> Released
        elif not current_state and self.last_state:
            self.released_time = now
            duration = self.released_time - self.pressed_time
            
            if duration >= self.long_press_threshold:
                # It was a long press, clear double click wait
                event = EVENT_LONG
                self.waiting_for_double = False
            else:
                # It was a short press
                if self.waiting_for_double:
                    # This is the second press!
                    event = EVENT_DOUBLE
                    self.waiting_for_double = False
                else:
                    # First short press. We don't emit yet, we wait.
                    self.waiting_for_double = True
        
        # If we are waiting for a double press and time expires, emit single short press
        if self.waiting_for_double and not current_state:
            if now - self.released_time > self.double_click_threshold:
                event = EVENT_SHORT
                self.waiting_for_double = False
                
        self.last_state = current_state
        return event
