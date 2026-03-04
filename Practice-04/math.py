import math
def deg_to_rad():
    deg = int(input("Input degree: "))
    rad = deg * (math.pi / 180)
    print("Output radian:",rad)
def trapezoid_area():
    height = int(input("Height: "))
    base1 = int(input("Base, first value: "))
    base2 = int(input("Base, second value: "))
    area=((base1+base2)/2)*height
    print("Expected Output:",area)
def reg_pol_area():
    n = int(input("Input number of sides: "))
    length = int(input("Input the length of a side: "))
    area = (n * length**2) / (4 * math.tan(math.pi / n))
    print("The area of the polygon is: ",area)
def parallelogram_area():
    length = int(input("Length of base: "))
    height = int(input("Height of parallelogram: "))
    area=float(length*height)
    print("Expected Output:",area)
deg_to_rad()
trapezoid_area()
reg_pol_area()
parallelogram_area()