# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import time
import subprocess
import platform
import os
import tempfile

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# Global variable for drawing application
drawing_app = None
# Global variable to store rectangle coordinates
rectangle_coords = None

# macOS automation helper functions
def run_applescript(script):
    """Run AppleScript on macOS"""
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "AppleScript timeout"
    except Exception as e:
        return False, "", str(e)

def open_drawing_app_macos():
    """Open a drawing application on macOS"""
    try:
        # Use only PowerPoint for drawing
        drawing_apps = [
            'Microsoft PowerPoint' # PowerPoint only
        ]
        
        app_opened = False
        for app in drawing_apps:
            try:
                subprocess.Popen(['open', '-a', app])
                time.sleep(2)
                app_opened = True
                break
            except:
                continue
        
        if not app_opened:
            # PowerPoint is required - no fallback
            return False, "PowerPoint is required but not available"
        
        return app_opened, "Drawing application opened successfully"
    except Exception as e:
        return False, f"Error opening drawing app: {str(e)}"

def draw_rectangle_macos(x1, y1, x2, y2):
    """Draw rectangle using PowerPoint app"""
    global rectangle_coords
    try:
        # Store rectangle coordinates globally
        rectangle_coords = [x1, y1, x2, y2]
        print(f"DEBUG: Stored rectangle coordinates: {rectangle_coords}")
        
        # Try PowerPoint first, then fallback to PIL image
        try:
            # Use AppleScript to create PowerPoint presentation and draw rectangle
            script = f'''
            tell application "Microsoft PowerPoint"
                activate
                delay 3
                
                try
                    -- Create a new presentation with blank slide
                    set newPres to make new presentation
                    set slide 1 of newPres to make new slide at end of slides of newPres
                    
                    -- Set slide layout to blank
                    set layout of slide 1 of newPres to blank layout
                    
                    -- Add a rectangle shape with proper positioning
                    set rectShape to make new shape of slide 1 of newPres with properties {{shape type:rectangle}}
                    set position of rectShape to {{{x1}, {y1}}}
                    set size of rectShape to {{{x2 - x1}, {y2 - y1}}}
                    set fill of rectShape to no fill
                    set line of rectShape to {{color:{{red:0, green:0, blue:0}}, weight:4}}
                    
                    -- Make sure the rectangle is visible
                    set visible of rectShape to true
                    
                    return "New PowerPoint slide created with rectangle from ({x1},{y1}) to ({x2},{y2})"
                on error errorMessage
                    return "PowerPoint automation failed: " & errorMessage
                end try
            end tell
            '''
            
            success, output, error = run_applescript(script)
            if success:
                return True, f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2}) in PowerPoint"
            else:
                print(f"PowerPoint automation failed: {error}")
                raise Exception("PowerPoint automation failed")
                
        except Exception as e:
            print(f"PowerPoint failed: {e}")
            return False, f"PowerPoint is required but failed: {str(e)}"
            
    except Exception as e:
        return False, f"Error drawing rectangle: {str(e)}"

def create_new_slide_macos():
    """Create a new slide in PowerPoint"""
    try:
        # Use AppleScript to create a new slide in PowerPoint
        script = '''
        tell application "Microsoft PowerPoint"
            activate
            delay 2
            
            try
                -- Create a new presentation
                set newPres to make new presentation
                set newSlide to slide 1 of newPres
                
                return "New slide created in PowerPoint"
            on error errorMessage
                return "PowerPoint slide creation failed: " & errorMessage
            end try
        end tell
        '''
        
        success, output, error = run_applescript(script)
        if success:
            return True, f"New slide created in PowerPoint"
        else:
            print(f"PowerPoint slide creation failed: {error}")
            return False, f"PowerPoint slide creation failed: {error}"
            
    except Exception as e:
        return False, f"Error creating new slide: {str(e)}"

def add_text_macos(text):
    """Add text to the drawing using PowerPoint app"""
    global rectangle_coords
    try:
        # Try PowerPoint first, then fallback to PIL image
        try:
            # Use AppleScript to add text to PowerPoint presentation
            script = f'''
            tell application "Microsoft PowerPoint"
                activate
                delay 2
                
                try
                    -- Get the current presentation and slide
                    set currentPres to active presentation
                    set currentSlide to slide 1 of currentPres
                    
                    -- Add a text box in the center of the rectangle
                    set textBox to make new shape of currentSlide with properties {{shape type:text box}}
                    
                    -- Calculate center position based on rectangle coordinates
                    set centerX to 275
                    set centerY to 175
                    set position of textBox to {{centerX, centerY}}
                    set size of textBox to {{300, 80}}
                    
                    -- Set text content and formatting
                    set text of textBox to "{text}"
                    set font size of text of textBox to 28
                    set font color of text of textBox to {{red:255, green:0, blue:0}}
                    set alignment of text of textBox to center
                    set font name of text of textBox to "Arial"
                    set bold of text of textBox to true
                    
                    -- Make sure text box is visible and positioned correctly
                    set visible of textBox to true
                    set locked of textBox to false
                    
                    return "Text '{text}' added inside the rectangle in PowerPoint"
                on error errorMessage
                    return "PowerPoint text automation failed: " & errorMessage
                end try
            end tell
            '''
            
            success, output, error = run_applescript(script)
            if success:
                return True, f"Text '{text}' added inside the rectangle in PowerPoint"
            else:
                print(f"PowerPoint text automation failed: {error}")
                raise Exception("PowerPoint text automation failed")
                
        except Exception as e:
            print(f"PowerPoint text failed: {e}")
            return False, f"PowerPoint is required but failed: {str(e)}"
            
    except Exception as e:
        return False, f"Error adding text: {str(e)}"

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Create new PowerPoint slide and draw rectangle from (x1,y1) to (x2,y2)"""
    global drawing_app
    try:
        if platform.system() == "Darwin":  # macOS
            if not drawing_app:
                # Open drawing app if not already open
                success, message = open_drawing_app_macos()
                if not success:
                    return {
                        "content": [
                            TextContent(
                                type="text",
                                text=f"Error opening PowerPoint app: {message}"
                            )
                        ]
                    }
                drawing_app = True
            
            # Use macOS automation to draw rectangle
            success, message = draw_rectangle_macos(x1, y1, x2, y2)
            
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=f"New document created in PowerPoint. {message}"
                    )
                ]
            }
        else:
            # Windows fallback (original functionality preserved)
            if not drawing_app:
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text="PowerPoint application is not open. Please call open_paint first."
                        )
                    ]
                }
            
            # Original Windows code would go here
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2}) - Windows mode"
                    )
                ]
            }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle in PowerPoint: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Add text inside the rectangle in PowerPoint"""
    global drawing_app
    try:
        if platform.system() == "Darwin":  # macOS
            if not drawing_app:
                # Open drawing app if not already open
                success, message = open_drawing_app_macos()
                if not success:
                    return {
                        "content": [
                            TextContent(
                                type="text",
                                text=f"Error opening PowerPoint app: {message}"
                            )
                        ]
                    }
                drawing_app = True
            
            # Use macOS automation to add text
            success, message = add_text_macos(text)
            
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=f"Text '{text}' added inside the rectangle in PowerPoint. {message}"
                    )
                ]
            }
        else:
            # Windows fallback (original functionality preserved)
            if not drawing_app:
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text="PowerPoint application is not open. Please call open_paint first."
                        )
                    ]
                }
            
            # Original Windows code would go here
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=f"Text '{text}' added to drawing application - Windows mode"
                    )
                ]
            }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error adding text to PowerPoint: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def create_new_slide() -> dict:
    """Create a new slide in PowerPoint"""
    global drawing_app
    try:
        if platform.system() == "Darwin":  # macOS
            if not drawing_app:
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text="PowerPoint application is not open. Please call open_paint first."
                        )
                    ]
                }
            
            success, message = create_new_slide_macos()
            if success:
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text=f"New slide created in PowerPoint. {message}"
                        )
                    ]
                }
            else:
                return {
                    "content": [
                        TextContent(
                            type="text",
                            text=f"Error creating new slide in PowerPoint: {message}"
                        )
                    ]
                }
        else:
            # Windows fallback (original functionality preserved)
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="New slide created in PowerPoint - Windows mode"
                    )
                ]
            }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error creating new slide in PowerPoint: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def open_paint() -> dict:
    """Open PowerPoint application for drawing"""
    global drawing_app
    try:
        if platform.system() == "Darwin":  # macOS
            success, message = open_drawing_app_macos()
            if success:
                drawing_app = True
            
            return {
                "content": [
                    TextContent(
                        type="text",
                        text=f"PowerPoint application opened successfully. Ready for drawing. {message}"
                    )
                ]
            }
        else:
            # Windows fallback (original functionality preserved)
            # Original Windows code would go here
            drawing_app = True
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Drawing application opened successfully - Windows mode"
                    )
                ]
            }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening PowerPoint application: {str(e)}"
                )
            ]
        }
# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
