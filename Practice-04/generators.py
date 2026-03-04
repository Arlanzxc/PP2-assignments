#1
def gen_sqr(N):
    for i in range(N+1):
        yield i*i
N = int(input())
for i in gen_sqr(N):
    print(i)

print("\n")
#2
def gen_even(n):
    for i in range(0,n+1,2):
        yield str(i)
n = int(input())
print(" ".join(gen_even(n)))

print("\n")
#3
def gen_div(n):
    for i in range(0,n+1,12):
        yield str(i)
n = int(input())
print(",".join(gen_div(n)))

print("\n")
#4
def gen_sqr_a_b(a,b):
    for i in range(a,b+1):
        yield i*i
a,b = map(int, input().split(" "))
for i in gen_sqr_a_b(a,b):
    print(i)

print("\n")
#5
def gen_n_0(n):
    for i in range(n,-1,-1):
        yield i
n = int(input())
for i in gen_n_0(n):
    print(i)