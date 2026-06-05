import time
import random

class Behavior:
    def __init__(self, eyes):
        self.eyes = eyes
        self.state = "IDLE"
        self.state_start_time = time.monotonic()
        self.next_action_time = self.state_start_time + random.uniform(2.0, 5.0)
        
        # Blinking state variables
        self.blink_start = 0
        self.blink_duration = 0.1 # seconds (faster blink)
        self.is_blinking = False
        self.next_blink_time = self.state_start_time + random.uniform(3.0, 5.0)
        
        # Fluid animation targets
        self.current_x = 0.0
        self.current_y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        
        self.start_x = 0.0
        self.start_y = 0.0
        
        self.current_squint = 1.0
        self.target_squint = 1.0
        self.start_squint = 1.0
        
        self.current_cheek = 0.0
        self.target_cheek = 0.0
        self.start_cheek = 0.0
        
        self.move_start_time = self.state_start_time
        self.move_duration = 0.15 # seconds (faster, snappy cartoony movement)
        
    def update(self):
        now = time.monotonic()
        
        # 1. Check if it's time to change behavior state
        if now >= self.next_action_time:
            self.change_state()
            
        # 2. Set targets based on state
        if self.state == "IDLE":
            self.target_x = 0.0
            self.target_y = 0.0
            self.target_squint = 1.0
            self.target_cheek = 0.0
        elif self.state == "LOOK_LEFT":
            self.target_x = -12.0
            self.target_y = 0.0
            self.target_squint = 1.0
            self.target_cheek = 0.0
        elif self.state == "LOOK_RIGHT":
            self.target_x = 12.0
            self.target_y = 0.0
            self.target_squint = 1.0
            self.target_cheek = 0.0
        elif self.state == "HAPPY":
            self.target_x = 0.0
            self.target_y = 0.0
            self.target_squint = 1.0 # Eyes fully open
            self.target_cheek = 1.0  # Big smile cheeks!
        elif self.state == "NAPPING":
            self.target_x = 0.0
            self.target_y = 0.0
            self.target_squint = 0.0 # Fully closed to a line
            self.target_cheek = 0.0
            
        # 3. Interpolate current positions towards targets using Disney ease-in-out
        move_progress = (now - self.move_start_time) / self.move_duration
        if move_progress >= 1.0:
            move_progress = 1.0
            self.current_x = self.target_x
            self.current_y = self.target_y
            self.current_squint = self.target_squint
            self.current_cheek = self.target_cheek
        else:
            eased_p = self.ease_in_out_cubic(move_progress)
            self.current_x = self.start_x + (self.target_x - self.start_x) * eased_p
            self.current_y = self.start_y + (self.target_y - self.start_y) * eased_p
            self.current_squint = self.start_squint + (self.target_squint - self.start_squint) * eased_p
            self.current_cheek = self.start_cheek + (self.target_cheek - self.start_cheek) * eased_p
        
        self.eyes.look(int(self.current_x), int(self.current_y))
        
        # 4. Handle fast blinking over the top of the squint
        blink_value = 1.0
        if self.is_blinking:
            progress = (now - self.blink_start) / self.blink_duration
            if progress >= 1.0:
                self.is_blinking = False
            else:
                # Eased V-shape blink
                if progress < 0.5:
                    blink_value = 1.0 - self.ease_in_out_cubic(progress * 2)
                else:
                    blink_value = self.ease_in_out_cubic((progress - 0.5) * 2)
        else:
            if now >= self.next_blink_time:
                self.is_blinking = True
                self.blink_start = now
                self.next_blink_time = now + random.uniform(3.0, 5.0)
                
        # The eye open amount is the minimum of the squint and the blink
        self.eyes.blink(min(self.current_squint, blink_value), self.current_cheek)
                
    def change_state(self):
        # Save current positions as the start for the new easing animation
        self.start_x = self.current_x
        self.start_y = self.current_y
        self.start_squint = self.current_squint
        self.start_cheek = self.current_cheek
        self.move_start_time = time.monotonic()
        
        # We weigh IDLE more heavily so it doesn't look too erratic
        # 1. Pick next state: always return to IDLE between actions
        if self.state != "IDLE":
            self.state = "IDLE"
        else:
            action_states = ["LOOK_LEFT", "LOOK_RIGHT", "HAPPY", "NAPPING"]
            self.state = random.choice(action_states)
        self.state_start_time = time.monotonic()
        
        # Determine how long to stay in this state
        if self.state == "IDLE":
            self.next_action_time = self.state_start_time + random.uniform(1.0, 4.0)
        elif self.state == "NAPPING":
            self.next_action_time = self.state_start_time + random.uniform(4.0, 8.0)
        elif self.state == "HAPPY":
            self.next_action_time = self.state_start_time + random.uniform(4.0, 6.0)
        else:
            self.next_action_time = self.state_start_time + random.uniform(0.5, 1.5)

    def ease_in_out_cubic(self, t):
        if t < 0.5:
            return 4 * t * t * t
        else:
            p = 2 * t - 2
            return 0.5 * p * p * p + 1
