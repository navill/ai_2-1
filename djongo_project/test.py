class A:
    attr = []

    def __init__(self):
        print('???',self.attr)


class B(A):
    attr = [1, 2, 3, 4, 5, 7, 8, 9, 10]


a = A()
a.attr = 1234
print(a.attr)
b = B()
b.attr = 4567
print(b.attr)
