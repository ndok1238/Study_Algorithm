"""간단한 계산 함수 모음 (브랜치 연습용)."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("[A] 나누는 수는 0이 될 수 없습니다")
    return a / b
