"""
MCP Server with Browser Drawing Tools
Provides mathematical tools and browser-based drawing capabilities
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import math
import sys
import subprocess
import webbrowser
import os
import time
from pathlib import Path

# Initialize MCP server
mcp = FastMCP("BrowserDrawingCalculator")

# Global state
browser_opened = False
canvas_html_path = None
last_rectangle_coords = None
current_text = None
favorite_color_global = "blue"


def create_canvas_html(favorite_color: str = "blue", rectangle_coords: tuple = None, text_to_draw: str = None) -> str:
    """
    Create an HTML file with a canvas for drawing
    
    Args:
        favorite_color: Color to use for drawing
        rectangle_coords: Optional tuple of (x1, y1, x2, y2) to draw rectangle immediately
        text_to_draw: Optional text to draw in the rectangle
        
    Returns:
        Path to the HTML file
    """
    # Build auto-draw script if coordinates provided
    auto_draw_script = ""
    if rectangle_coords:
        x1, y1, x2, y2 = rectangle_coords
        auto_draw_script = f"window.drawRectangle({x1}, {y1}, {x2}, {y2});"
        if text_to_draw:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            # Escape single quotes in text
            escaped_text = str(text_to_draw).replace("'", "\\'")
            auto_draw_script += f"\nwindow.addText('{escaped_text}', {center_x}, {center_y});"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Drawing Canvas</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }}
        #canvas {{
            border: 3px solid {favorite_color};
            border-radius: 10px;
            display: block;
            background: #f9f9f9;
            cursor: crosshair;
        }}
        .info {{
            margin-top: 15px;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 8px;
            font-size: 14px;
        }}
        .status {{
            text-align: center;
            margin-top: 10px;
            color: {favorite_color};
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 AI Agent Drawing Canvas</h1>
        <canvas id="canvas" width="800" height="600"></canvas>
        <div class="info">
            <strong>Status:</strong> <span id="status">Ready for drawing commands...</span>
        </div>
        <div class="status">Using your favorite color: {favorite_color}</div>
    </div>
    
    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const status = document.getElementById('status');
        
        // Store drawing state
        window.drawingState = {{
            rectangles: [],
            texts: [],
            favoriteColor: '{favorite_color}'
        }};
        
        // Function to draw rectangle
        window.drawRectangle = function(x1, y1, x2, y2) {{
            const width = x2 - x1;
            const height = y2 - y1;
            
            // Draw filled rectangle with user's favorite color
            ctx.fillStyle = window.drawingState.favoriteColor + '40'; // Semi-transparent
            ctx.fillRect(x1, y1, width, height);
            
            // Draw border
            ctx.strokeStyle = window.drawingState.favoriteColor;
            ctx.lineWidth = 4;
            ctx.strokeRect(x1, y1, width, height);
            
            window.drawingState.rectangles.push({{x1, y1, x2, y2}});
            status.textContent = `Rectangle drawn from (${{x1}},${{y1}}) to (${{x2}},${{y2}})`;
            
            return true;
        }};
        
        // Function to add text
        window.addText = function(text, x, y) {{
            ctx.font = 'bold 48px Arial';
            ctx.fillStyle = window.drawingState.favoriteColor;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // Add text shadow for better visibility
            ctx.shadowColor = 'rgba(0,0,0,0.3)';
            ctx.shadowBlur = 4;
            ctx.shadowOffsetX = 2;
            ctx.shadowOffsetY = 2;
            
            ctx.fillText(text, x, y);
            
            // Reset shadow
            ctx.shadowColor = 'transparent';
            
            window.drawingState.texts.push({{text, x, y}});
            status.textContent = `Text "${{text}}" added at (${{x}},${{y}})`;
            
            return true;
        }};
        
        // Function to clear canvas
        window.clearCanvas = function() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            window.drawingState.rectangles = [];
            window.drawingState.texts = [];
            status.textContent = 'Canvas cleared';
            return true;
        }};
        
        // Auto-execute drawing commands if provided
        {auto_draw_script}
        
        console.log('Canvas ready for drawing!');
        console.log('Use window.drawRectangle(x1, y1, x2, y2) to draw');
        console.log('Use window.addText(text, x, y) to add text');
    </script>
</body>
</html>"""
    
    # Create temp file
    temp_dir = Path("/tmp")
    html_file = temp_dir / f"agent_canvas_{int(time.time())}.html"
    html_file.write_text(html_content)
    
    return str(html_file)


# ==================== MATHEMATICAL TOOLS ====================

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return int(a + b)


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return int(a - b)


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return int(a * b)


@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return float(a / b)


@mcp.tool()
def power(a: int, b: int) -> int:
    """Calculate a to the power of b"""
    return int(a ** b)


@mcp.tool()
def sqrt(a: int) -> float:
    """Calculate square root of a number"""
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return float(math.sqrt(a))


@mcp.tool()
def factorial(a: int) -> int:
    """Calculate factorial of a number"""
    if a < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return int(math.factorial(a))


@mcp.tool()
def add_list(numbers: list) -> int:
    """Add all numbers in a list"""
    return sum(numbers)


@mcp.tool()
def strings_to_chars_to_int(text: str) -> list:
    """Convert string characters to ASCII values"""
    return [ord(char) for char in text]


@mcp.tool()
def int_list_to_exponential_sum(numbers: list) -> float:
    """Calculate sum of exponentials of numbers in a list"""
    return sum(math.exp(i) for i in numbers)


# ==================== BROWSER DRAWING TOOLS ====================

@mcp.tool()
async def open_browser(favorite_color: str = "blue") -> dict:
    """
    Open a web browser with a drawing canvas
    
    Args:
        favorite_color: User's favorite color for drawing (default: blue)
    """
    global browser_opened, canvas_html_path, favorite_color_global
    
    try:
        # Store favorite color globally
        favorite_color_global = favorite_color
        
        # Create HTML canvas
        canvas_html_path = create_canvas_html(favorite_color)
        
        # Open in browser
        webbrowser.open(f"file://{canvas_html_path}")
        
        browser_opened = True
        time.sleep(2)  # Give browser time to open
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Browser opened with drawing canvas. Using color: {favorite_color}. Canvas ready for drawing!"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening browser: {str(e)}"
                )
            ]
        }


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """
    Draw a rectangle on the canvas
    
    Args:
        x1: Left x coordinate
        y1: Top y coordinate
        x2: Right x coordinate
        y2: Bottom y coordinate
    """
    global browser_opened, last_rectangle_coords, canvas_html_path, favorite_color_global, current_text
    
    if not browser_opened:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Browser not opened. Please call open_browser first."
                )
            ]
        }
    
    try:
        # Store coordinates for text placement
        last_rectangle_coords = (x1, y1, x2, y2)
        
        # Regenerate HTML with rectangle (and text if available)
        canvas_html_path = create_canvas_html(
            favorite_color=favorite_color_global,
            rectangle_coords=(x1, y1, x2, y2),
            text_to_draw=current_text
        )
        
        # Open the new HTML file
        webbrowser.open(f"file://{canvas_html_path}")
        time.sleep(1)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2}) on the canvas"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }


@mcp.tool()
async def add_text_to_canvas(text: str) -> dict:
    """
    Add text to the center of the last drawn rectangle
    
    Args:
        text: Text to display on the canvas
    """
    global browser_opened, last_rectangle_coords, canvas_html_path, favorite_color_global, current_text
    
    if not browser_opened:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Browser not opened. Please call open_browser first."
                )
            ]
        }
    
    if not last_rectangle_coords:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="No rectangle drawn yet. Please call draw_rectangle first."
                )
            ]
        }
    
    try:
        # Store the text
        current_text = text
        
        # Calculate center of rectangle
        x1, y1, x2, y2 = last_rectangle_coords
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Regenerate HTML with both rectangle and text
        canvas_html_path = create_canvas_html(
            favorite_color=favorite_color_global,
            rectangle_coords=last_rectangle_coords,
            text_to_draw=text
        )
        
        # Open the new HTML file
        webbrowser.open(f"file://{canvas_html_path}")
        time.sleep(1)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text '{text}' added to canvas at center of rectangle ({center_x},{center_y})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error adding text: {str(e)}"
                )
            ]
        }


@mcp.tool()
async def clear_canvas() -> dict:
    """Clear the drawing canvas"""
    global browser_opened, last_rectangle_coords
    
    if not browser_opened:
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Browser not opened. Please call open_browser first."
                )
            ]
        }
    
    try:
        applescript = """
        tell application "Safari"
            activate
            do JavaScript "window.clearCanvas()" in current tab of window 1
        end tell
        """
        
        try:
            subprocess.run(['osascript', '-e', applescript], capture_output=True, timeout=5)
        except:
            pass
        
        last_rectangle_coords = None
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Canvas cleared successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error clearing canvas: {str(e)}"
                )
            ]
        }


if __name__ == "__main__":
    print("Starting MCP Browser Drawing Server...")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")

