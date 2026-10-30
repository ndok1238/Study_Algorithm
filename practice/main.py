from calc import add, subtract, multiply, divide
from utils import greet, total, average


def main():
    print(greet("Git"))
    print("add:", add(6, 3))
    print("subtract:", subtract(6, 3))
    print("multiply:", multiply(6, 3))
    print("divide:", divide(6, 3))
    print("total:", total([1, 2, 3, 4]))
    print("average1:", average([1, 2, 3, 4]))
    print("average2:", average([1, 2, 3, 4]))


if __name__ == "__main__":
    main()
