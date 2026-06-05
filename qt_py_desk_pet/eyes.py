import displayio
import vectorio
import math

class Eyes:
    def __init__(self, display_width, display_height):
        self.width = display_width
        self.height = display_height
        
        # Color palettes
        # The eye shapes will use fg_palette (white)
        self.fg_palette = displayio.Palette(2)
        self.fg_palette[0] = 0x000000 # Transparent background
        self.fg_palette[1] = 0xFFFFFF # White
        
        # The eyelids will use bg_palette (black) to hide the eyes when blinking
        self.bg_palette = displayio.Palette(2)
        self.bg_palette[0] = 0x000000
        self.bg_palette[1] = 0x000000 # Black
        
        self.group = displayio.Group()
        
        # Eye parameters (oval shape)
        self.eye_rx = 12
        self.eye_ry = 20
        self.eye_spacing = 48
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # Pre-calculate points for an oval polygon
        oval_points = []
        num_points = 24
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            oval_points.append((int(math.cos(angle) * self.eye_rx), int(math.sin(angle) * self.eye_ry)))
        
        # Left eye
        self.left_eye = vectorio.Polygon(pixel_shader=self.fg_palette, points=oval_points)
        self.left_eye.x = self.center_x - self.eye_spacing // 2
        self.left_eye.y = self.center_y
        
        # Right eye
        self.right_eye = vectorio.Polygon(pixel_shader=self.fg_palette, points=oval_points)
        self.right_eye.x = self.center_x + self.eye_spacing // 2
        self.right_eye.y = self.center_y
        
        # Eyelids (top and bottom black rectangles that close to the middle)
        self.eyelid_width = self.eye_rx * 2 + 8
        self.eyelid_height = self.eye_ry + 8
        
        self.left_eyelid_top = vectorio.Rectangle(pixel_shader=self.bg_palette, width=self.eyelid_width, height=self.eyelid_height)
        self.left_eyelid_bottom = vectorio.Rectangle(pixel_shader=self.bg_palette, width=self.eyelid_width, height=self.eyelid_height)
        
        self.right_eyelid_top = vectorio.Rectangle(pixel_shader=self.bg_palette, width=self.eyelid_width, height=self.eyelid_height)
        self.right_eyelid_bottom = vectorio.Rectangle(pixel_shader=self.bg_palette, width=self.eyelid_width, height=self.eyelid_height)
        
        # Cheeks (black circles that rise from the bottom to create a smile curve)
        self.cheek_radius = 24
        self.left_cheek = vectorio.Circle(radius=self.cheek_radius, pixel_shader=self.bg_palette)
        self.right_cheek = vectorio.Circle(radius=self.cheek_radius, pixel_shader=self.bg_palette)
        
        # Add to group in order (eye -> cheek -> eyelid)
        self.group.append(self.left_eye)
        self.group.append(self.right_eye)
        self.group.append(self.left_cheek)
        self.group.append(self.right_cheek)
        self.group.append(self.left_eyelid_top)
        self.group.append(self.left_eyelid_bottom)
        self.group.append(self.right_eyelid_top)
        self.group.append(self.right_eyelid_bottom)
        
        # Initial position
        self.look(0, 0)
        self.blink(1.0, 0.0)
        
    def blink(self, open_amount=1.0, cheek_amount=0.0):
        """
        open_amount: 1.0 is fully open, 0.0 is fully closed.
        cheek_amount: 0.0 is hidden, 1.0 is fully raised (smiling).
        """
        # Ensure it doesn't close 100% so a white line remains when closed
        open_amount = max(0.1, min(1.0, open_amount))
        # Top eyelid drops down, bottom eyelid rises up
        drop = int((1.0 - open_amount) * (self.eye_ry + 4))
        
        self.left_eyelid_top.y = self.left_eyelid_top_base_y - self.eyelid_height + drop
        self.left_eyelid_bottom.y = self.left_eyelid_bottom_base_y - drop
        
        self.right_eyelid_top.y = self.right_eyelid_top_base_y - self.eyelid_height + drop
        self.right_eyelid_bottom.y = self.right_eyelid_bottom_base_y - drop
        
        # Raise cheeks
        cheek_rise = int(cheek_amount * 12)
        self.left_cheek.y = self.left_cheek_base_y - cheek_rise
        self.right_cheek.y = self.right_cheek_base_y - cheek_rise
        
    def look(self, x_offset, y_offset):
        """
        Moves the eyes relative to the center.
        """
        self.left_eye.x = (self.center_x - self.eye_spacing // 2) + x_offset
        self.left_eye.y = self.center_y + y_offset
        self.right_eye.x = (self.center_x + self.eye_spacing // 2) + x_offset
        self.right_eye.y = self.center_y + y_offset
        
        # Update cheek bases (offset towards outside)
        cheek_offset_x = 6
        self.left_cheek.x = self.left_eye.x - cheek_offset_x
        self.left_cheek_base_y = self.left_eye.y + self.eye_ry + self.cheek_radius
        
        self.right_cheek.x = self.right_eye.x + cheek_offset_x
        self.right_cheek_base_y = self.right_eye.y + self.eye_ry + self.cheek_radius
        
        # Update eyelid bases so they follow the eye movement
        self.left_eyelid_top.x = self.left_eye.x - self.eye_rx - 4
        self.left_eyelid_top_base_y = self.left_eye.y - self.eye_ry - 4
        
        self.left_eyelid_bottom.x = self.left_eye.x - self.eye_rx - 4
        self.left_eyelid_bottom_base_y = self.left_eye.y + self.eye_ry + 4
        
        self.right_eyelid_top.x = self.right_eye.x - self.eye_rx - 4
        self.right_eyelid_top_base_y = self.right_eye.y - self.eye_ry - 4
        
        self.right_eyelid_bottom.x = self.right_eye.x - self.eye_rx - 4
        self.right_eyelid_bottom_base_y = self.right_eye.y + self.eye_ry + 4
