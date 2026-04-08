a = 5

print(a > 0 and a < 10)

b = 5

print(b < 5 or b > 10)

c = 5

print(not(c > 3 and c < 10))

x = ["apple", "banana"]
y = ["apple", "banana"]
z = x

# Identity Operators
print(x is z)
print(x is y)
print(x == y)
print(x is not y)

# Membership Operators
print("banana" in x)
print("pineapple" not in y)