import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Create the model
model = genai.GenerativeModel('gemini-2.0-flash')

# system prompt ansd query
system_prompt = """You are a stock agent solving problems in iterations. Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: python_function_name|input
2. FINAL_ANSWER: [number]

where python_function_name is one of the following:
1. get_price: takes the stock ticker (e.g., "MSFT"), creates a ticker object and gets the current price
2. print_price: takes the stock ticker (e.g., "MSFT"), gets the price internally, and prints it

IMPORTANT: Both functions take the SAME ticker symbol as input. Do NOT pass price values to print_price.
DO NOT include multiple responses. Give ONE response at a time."""

query = "Get the stock price of Google (GOOG)"

# Function definitions
def get_price(ticker):
    import yfinance as yf
    ticker_object = yf.Ticker(ticker)
    current_price = ticker_object.fast_info.last_price
    return current_price

def print_price(ticker):
    # Get the price using the get_price function
    price = get_price(ticker)
    # Store the price in a variable
    stored_price = price
    # Print the price
    print(f"The current price of {ticker} is ${stored_price:.2f}")
    return f"The current price of {ticker} is ${stored_price:.2f}"

# Function caller
def function_caller(func_name, params):
    """Simple function caller that maps function names to actual functions"""
    function_map = {
        "get_price": get_price,
        "print_price": print_price
    }
    if func_name in function_map:
        return function_map[func_name](params)
    else:
        return f"Function {func_name} not found"

# Main execution
def run_stock_agent():
    prompt = f"{system_prompt}\n\nQuery: {query}"
    
    # First iteration
    response = model.generate_content(prompt)
    print(f"AI Response: {response.text}")
    
    # Check if it's a function call
    if response.text.startswith("FUNCTION_CALL:"):
        parts = response.text.split("|")
        if len(parts) == 2:
            func_name = parts[0].replace("FUNCTION_CALL: ", "").strip()
            params = parts[1].strip()
            
            print(f"Calling function: {func_name} with params: {params}")
            iteration_result = function_caller(func_name, params)
            print(f"Function result: {iteration_result}")
            
            # Second iteration with result
            iteration_2 = f"In the first iteration you called {func_name} with {params} parameters, and the function returned {iteration_result}. What should I do next?"
            prompt_2 = f"{system_prompt}\n\nQuery: {query}\n\n{iteration_2}"
            
            response_2 = model.generate_content(prompt_2)
            print(f"AI Response: {response_2.text}")
            
            # If it's another function call, execute it
            if response_2.text.startswith("FUNCTION_CALL:"):
                parts_2 = response_2.text.split("|")
                if len(parts_2) == 2:
                    func_name_2 = parts_2[0].replace("FUNCTION_CALL: ", "").strip()
                    params_2 = parts_2[1].strip()
                    
                    print(f"Calling function: {func_name_2} with params: {params_2}")
                    iteration_result_2 = function_caller(func_name_2, params_2)
                    print(f"Function result: {iteration_result_2}")
            elif response_2.text.startswith("FINAL_ANSWER:"):
                print(f"Final answer: {response_2.text}")
        else:
            print("Invalid function call format")
    elif response.text.startswith("FINAL_ANSWER:"):
        print(f"Final answer: {response.text}")
    else:
        print("Unexpected response format")

# Run the stock agent
run_stock_agent()