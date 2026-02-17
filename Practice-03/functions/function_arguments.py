def my_function(fname):
  print(fname + " Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")

def function(name): # name is a parameter
  print("Hello", name)

function("Emil") # "Emil" is an argument

def my_func(fname, lname):
  print(fname + " " + lname)

my_func("Emil", "Refsnes")

# Default Parameter Values
def greet(name = "friend"):
  print("Hello", name)

greet("Emil")
greet("Tobias")
greet()
greet("Linus")

# Keyword Arguments
def animals(animal, name):
  print("I have a", animal)
  print("My", animal + "'s name is", name)
animals(animal = "dog", name = "Buddy")

# Tuple
def tuples():
  return (10, 20)

x, y = tuples()
print("x:", x)
print("y:", y)

# Positional-Only Arguments
def positional_only(name, /):
  print("Hello", name)

positional_only("Emil")

# Combining Positional-Only and Keyword-Only
def combining(a, b, /, *, c, d):
  return a + b + c + d

result = combining(5, 10, c = 15, d = 20)
print(result)