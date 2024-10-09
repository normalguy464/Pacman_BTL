from math import *
t = int(input())
sum = 0
while t>0:
    n = int(input())
    for i in range(0,int(sqrt(n))+1):
        while n%i==0:
            sum += i
            n//=i
    if n!=1: 
        sum += n
    t-=1
print(sum)
