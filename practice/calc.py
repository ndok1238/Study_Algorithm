"""간단한 계산 함수 모음 (브랜치 연습용)."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("[B] 0으로 나누기는 허용되지 않습니다")
    return a / b
