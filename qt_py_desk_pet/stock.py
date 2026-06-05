import displayio
import terminalio
from adafruit_display_text import label
import time
import os

def draw_line(bitmap, x0, y0, x1, y1, color):
    """Bresenham's Line Algorithm to draw a line on a displayio.Bitmap"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < bitmap.width and 0 <= y0 < bitmap.height:
            bitmap[x0, y0] = color
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

class StockTrackerApp:
    def __init__(self, width, height, symbol="AI", name="C3.AI"):
        self.width = width
        self.height = height
        self.symbol = symbol
        self.name = name
        self.group = displayio.Group()
        
        # UI Elements (Top Half)
        self.title_label = label.Label(terminalio.FONT, text=self.name, color=0xFFFFFF, x=12, y=17)
        self.price_label = label.Label(terminalio.FONT, text="--", color=0xFFFFFF, x=12, y=28)
        self.change_label = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=100, y=28)
        self.status_label = label.Label(terminalio.FONT, text="Waiting...", color=0xFFFFFF, x=100, y=17)
        
        self.group.append(self.title_label)
        self.group.append(self.price_label)
        self.group.append(self.change_label)
        # We can hide status or keep it small. Let's not append status_label to save space.
        
        # Sparkline (Bottom Half)
        self.chart_width = 104  # 128 - 24 (12px padding left/right)
        self.chart_height = 18  # reduced by 2px to add padding above
        self.chart_x = 12
        self.chart_y = 34
        self.bitmap = displayio.Bitmap(self.chart_width, self.chart_height, 2)
        self.palette = displayio.Palette(2)
        self.palette[0] = 0x000000 # Background
        self.palette[1] = 0xFFFFFF # Line color
        
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette, x=self.chart_x, y=self.chart_y)
        self.group.append(self.tile_grid)
        
        self.last_update_time = 0
        # Check every 5 minutes
        self.update_interval = 300 
        
        # Yahoo Finance API (Free, no key required)
        self.url = f"https://query1.finance.yahoo.com/v8/finance/chart/{self.symbol}?interval=15m&range=1d"
        
        self.requests = None
        self.wifi_connected = False
        
        self.mock_mode = os.getenv("WIFI_SSID") == "your_wifi_ssid"

    def setup_network(self):
        try:
            import wifi
            import ssl
            import socketpool
            import adafruit_requests
            
            if wifi.radio.connected:
                self.pool = socketpool.SocketPool(wifi.radio)
                self.requests = adafruit_requests.Session(self.pool, ssl.create_default_context())
                self.wifi_connected = True
        except ImportError:
            # Running in an environment without wifi module
            pass

    def update(self):
        now = time.monotonic()
        if self.last_update_time == 0 or now - self.last_update_time >= self.update_interval:
            self.last_update_time = now
            self.fetch_stock()
            
    def fetch_stock(self):
        if not self.requests:
            self.setup_network()
            
        if not self.wifi_connected:
            self.status_label.text = "No WiFi"
            return
            
            if self.mock_mode:
                self.status_label.text = "Mock"
                import random
                price = 150.00 + random.uniform(-2, 2)
                point_change = price - 150.0
                pct_change = (point_change / 150.0) * 100
                
                self.price_label.text = f"${price:.2f}"
                sign = "+" if point_change >= 0 else ""
                self.change_label.text = f"{sign}{pct_change:.1f}%"
                self.change_label.x = 128 - 12 - (len(self.change_label.text) * 6)
            
            # Generate mock sparkline array
            mock_prices = [150.0 + random.uniform(-2, 2) for _ in range(40)]
            mock_prices[-1] = price
            self.draw_sparkline(mock_prices)
            return
            
        self.status_label.text = "Fetching"
        try:
            response = self.requests.get(self.url)
            data = response.json()
            result = data.get("chart", {}).get("result", [])
            
            if result:
                meta = result[0].get("meta", {})
                current_price = meta.get("regularMarketPrice", 0)
                prev_close = meta.get("chartPreviousClose", 0)
                
                point_change = current_price - prev_close
                pct_change = (point_change / prev_close * 100) if prev_close > 0 else 0
                
                indicators = result[0].get("indicators", {})
                quote = indicators.get("quote", [])
                
                if quote:
                    closes = quote[0].get("close", [])
                    valid_closes = [c for c in closes if c is not None]
                    
                    if valid_closes:
                        self.price_label.text = f"${current_price:.2f}"
                        sign = "+" if point_change >= 0 else ""
                        self.change_label.text = f"{sign}{pct_change:.1f}%"
                        self.change_label.x = 128 - 12 - (len(self.change_label.text) * 6)
                        self.draw_sparkline(valid_closes)
                        response.close()
                        return
                        
            self.status_label.text = "Inv Data"
            response.close()
        except Exception as e:
            self.status_label.text = "Error"
            print("Fetch error:", e)

    def draw_sparkline(self, prices):
        # Clear bitmap
        for y in range(self.bitmap.height):
            for x in range(self.bitmap.width):
                self.bitmap[x, y] = 0
                
        if len(prices) < 2:
            return
            
        min_p = min(prices)
        max_p = max(prices)
        price_range = max_p - min_p
        if price_range == 0:
            price_range = 1
            
        step_x = (self.chart_width - 1) / (len(prices) - 1)
        
        last_px = None
        last_py = None
        
        for i, p in enumerate(prices):
            px = int(i * step_x)
            # Normalize to chart height (0 is top, height-1 is bottom)
            normalized = (p - min_p) / price_range
            py = int((self.chart_height - 1) - (normalized * (self.chart_height - 1)))
            
            if last_px is not None:
                draw_line(self.bitmap, last_px, last_py, px, py, 1)
                
            last_px = px
            last_py = py
