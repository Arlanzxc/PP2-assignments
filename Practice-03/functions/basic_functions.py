def my_function():
  print("Hello from a function")

def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

my_function()

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))

# Return value
def get_greeting():
  return "Hello from a function"

print(get_greeting())

# The pass statement
def function():
  pass
