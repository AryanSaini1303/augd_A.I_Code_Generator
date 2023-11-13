code_list = [
    ('\nprint("Hello World")\n',),
    ('\n# Function to calculate the sum of two numbers\ndef sum_two_numbers(num1, num2):\n    return num1 + num2\n\n# Taking user input for two numbers\nnum1 = float(input("Enter the first number: "))\nnum2 = float(input("Enter the second number: "))\n\n# Calling the function and printing the result\nresult = sum_two_numbers(num1, num2)\nprint("The sum is:", result)\n',)
]

for code_tuple in code_list:
    # Extracting the code from the tuple
    code = code_tuple[0]
    print(code)
