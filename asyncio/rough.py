from dis import dis
def square(
        x: int
) -> int:
    return x**2

def main():
    x = square(4)
    print(x)


print('square:')
dis(square)
print('main:')
dis(main)