import json

_functions_dict = {
    "multiply": {
        "name": "multiply",
        "description": ("Multiply two numbers."),
        "parameters": {
            "type": "object",
            "properties": {
                "number_one": {
                    "type": "number",
                    "description": "The first number to multiply.",
                },
                "number_two": {
                    "type": "number",
                    "description": "The second number to multiply.",
                },
            },
            "required": ["number_one", "number_two"],
        },
    }
}
functions = list(_functions_dict.values())  # Export for OpenAI as an array


def call_function(name: str, arguments: str) -> str:
    """Calls a function and returns the result."""

    # Ensure the function is defined
    if name not in _functions_dict:
        return "Function not defined."

    # Convert the function arguments from a string to a dict
    function_arguments_dict = json.loads(arguments)

    # Ensure the function arguments are valid
    function_parameters = _functions_dict[name]["parameters"]["properties"]
    for argument in function_arguments_dict:
        if argument not in function_parameters:
            return f"{argument} not defined."

    # Call the function and return the result
    return globals()[name](**function_arguments_dict)


def multiply(number_one: float, number_two: float) -> float:
    """Multiplies two numbers."""
    return f"The answer is {number_one * number_two}."
