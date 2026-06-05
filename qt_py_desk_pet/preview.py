import tkinter as tk
import time
import random

class PreviewDeskPet:
    def __init__(self, root):
        self.root = root
        self.root.title("Desk Pet Preview")
        
        # Scale up 3x for better visibility on desktop (original is 128x64)
        self.scale = 3
        self.width = 128 * self.scale
        self.height = 64 * self.scale
        
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        # Eye parameters
        self.eye_radius = 16 * self.scale
        self.eye_spacing = 48 * self.scale
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # Base values for eyes
        lx = self.center_x - self.eye_spacing // 2
        ly = self.center_y
        rx = self.center_x + self.eye_spacing // 2
        ry = self.center_y
        
        self.left_eye = self.canvas.create_oval(
            lx - self.eye_radius, ly - self.eye_radius,
            lx + self.eye_radius, ly + self.eye_radius,
            fill="white", outline="white"
        )
        
        self.right_eye = self.canvas.create_oval(
            rx - self.eye_radius, ry - self.eye_radius,
            rx + self.eye_radius, ry + self.eye_radius,
            fill="white", outline="white"
        )
        
        # Eyelids (black rectangles to cover eyes to simulate blinking)
        self.eyelid_w = (16 * 2 + 8) * self.scale
        self.eyelid_h = (16 * 2 + 8) * self.scale
        
        self.left_eyelid_base_y = ly - self.eye_radius - (4 * self.scale)
        self.left_eyelid = self.canvas.create_rectangle(
            lx - self.eye_radius - (4 * self.scale),
            self.left_eyelid_base_y - self.eyelid_h,
            lx - self.eye_radius - (4 * self.scale) + self.eyelid_w,
            self.left_eyelid_base_y,
            fill="black", outline="black"
        )
        
        self.right_eyelid_base_y = ry - self.eye_radius - (4 * self.scale)
        self.right_eyelid = self.canvas.create_rectangle(
            rx - self.eye_radius - (4 * self.scale),
            self.right_eyelid_base_y - self.eyelid_h,
            rx - self.eye_radius - (4 * self.scale) + self.eyelid_w,
            self.right_eyelid_base_y,
            fill="black", outline="black"
        )
        
        # State variables matching behavior.py
        self.state = "IDLE"
        self.state_start_time = time.time()
        self.next_action_time = self.state_start_time + random.uniform(2.0, 5.0)
        self.blink_start = 0
        self.blink_duration = 0.15
        self.is_blinking = False
        
        # Start update loop
        self.update_loop()

    def set_look(self, x_offset, y_offset):
        # Move eyes
        lx = (self.center_x - self.eye_spacing // 2) + x_offset * self.scale
        ly = self.center_y + y_offset * self.scale
        self.canvas.coords(self.left_eye, lx - self.eye_radius, ly - self.eye_radius, lx + self.eye_radius, ly + self.eye_radius)
        
        rx = (self.center_x + self.eye_spacing // 2) + x_offset * self.scale
        ry = self.center_y + y_offset * self.scale
        self.canvas.coords(self.right_eye, rx - self.eye_radius, ry - self.eye_radius, rx + self.eye_radius, ry + self.eye_radius)
        
        # Sync eyelid base Y to eye movement
        self.left_eyelid_base_y = ly - self.eye_radius - (4 * self.scale)
        ex_l = lx - self.eye_radius - (4 * self.scale)
        curr_l = self.canvas.coords(self.left_eyelid)
        # Keep same height, just move X and base Y
        self.canvas.coords(self.left_eyelid, ex_l, curr_l[1], ex_l + self.eyelid_w, curr_l[3])
        
        self.right_eyelid_base_y = ry - self.eye_radius - (4 * self.scale)
        ex_r = rx - self.eye_radius - (4 * self.scale)
        curr_r = self.canvas.coords(self.right_eyelid)
        self.canvas.coords(self.right_eyelid, ex_r, curr_r[1], ex_r + self.eyelid_w, curr_r[3])

    def set_blink(self, open_amount):
        open_amount = max(0.0, min(1.0, open_amount))
        # Amount to drop the eyelid
        drop = (1.0 - open_amount) * (self.eye_radius * 2 + 8 * self.scale)
        
        # update left eyelid
        cl = self.canvas.coords(self.left_eyelid)
        self.canvas.coords(self.left_eyelid, cl[0], self.left_eyelid_base_y - self.eyelid_h + drop, cl[2], self.left_eyelid_base_y + drop)
        
        # update right eyelid
        cr = self.canvas.coords(self.right_eyelid)
        self.canvas.coords(self.right_eyelid, cr[0], self.right_eyelid_base_y - self.eyelid_h + drop, cr[2], self.right_eyelid_base_y + drop)

    def change_state(self):
        states = ["IDLE", "IDLE", "IDLE", "LOOK_LEFT", "LOOK_RIGHT", "HAPPY"]
        self.state = random.choice(states)
        self.state_start_time = time.time()
        if self.state == "IDLE":
            self.next_action_time = self.state_start_time + random.uniform(1.0, 4.0)
        else:
            self.next_action_time = self.state_start_time + random.uniform(0.5, 1.5)

    def update_loop(self):
        now = time.time()
        
        if self.is_blinking:
            progress = (now - self.blink_start) / self.blink_duration
            if progress >= 1.0:
                self.is_blinking = False
                self.set_blink(1.0)
            else:
                if progress < 0.5:
                    self.set_blink(1.0 - (progress * 2))
                else:
                    self.set_blink((progress - 0.5) * 2)
        else:
            if random.random() < 0.03:
                self.is_blinking = True
                self.blink_start = now
                
        if now >= self.next_action_time:
            self.change_state()
            
        if self.state == "IDLE":
            if not self.is_blinking:
                self.set_look(0, 0)
                self.set_blink(1.0)
        elif self.state == "LOOK_LEFT":
            self.set_look(-12, 0)
            if not self.is_blinking:
                self.set_blink(1.0)
        elif self.state == "LOOK_RIGHT":
            self.set_look(12, 0)
            if not self.is_blinking:
                self.set_blink(1.0)
        elif self.state == "HAPPY":
            self.set_look(0, -6)
            if not self.is_blinking:
                self.set_blink(0.4)
                
        self.root.after(20, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = PreviewDeskPet(root)
    root.mainloop()
