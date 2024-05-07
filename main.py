# # # Function to add two numbers
# # def add(x, y):
# #     return x + y

# # # Function to subtract two numbers
# # def subtract(x, y):
# #     return x - y

# # # Function to multiply two numbers
# # def multiply(x, y):
# #     return x * y

# # # Function to divide two numbers
# # def divide(x, y):
# #     if y == 0:
# #         return "Cannot divide by zero"
# #     return x / y

# # print("Select operation:")
# # print("1. Add")
# # print("2. Subtract")
# # print("3. Multiply")
# # print("4. Divide")

# # while True:
# #     choice = '1'

# #     if choice in ('1', '2', '3', '4'):
# #         num1 = 5
# #         num2 = 5

# #         if choice == '1':
# #             print("Result:", add(num1, num2))
# #         elif choice == '2':
# #             print("Result:", subtract(num1, num2))
# #         elif choice == '3':
# #             print("Result:", multiply(num1, num2))
# #         elif choice == '4':
# #             print("Result:", divide(num1, num2))
        
# #         break
# #     else:
# #         print("Invalid Input")pip install fastapi uvicorn



# # main.py  
# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}
import os
from dotenv import load_dotenv,dotenv_values

load_dotenv()

print(os.getenv("MY_SECRET_KEY"))
print(os.getenv("COMBINED"))
print(os.getenv("MAIL"))