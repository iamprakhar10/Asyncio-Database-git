def mem_test():
    x=300
    y=300
    print(id(x))
    print(id(y))
    print(x is y)

mem_test()

from dataclasses import dataclass

@dataclass
class Trial:
    a: int
    b: int

a = Trial(1,2)
a.c = 3
print(a.c)