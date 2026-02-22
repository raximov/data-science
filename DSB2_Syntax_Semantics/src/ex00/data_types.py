def data_types():
    a = 42
    b = "hello"
    c = 3.14
    d = True
    e = [1, 2, 3]
    f = {"key": "value"}
    g = (1, 2)
    h = {1, 2, 3}
    types = [type(a).__name__, type(b).__name__, type(c).__name__, type(d).__name__, 
             type(e).__name__, type(f).__name__, type(g).__name__, type(h).__name__]
    print(types)


if __name__ == '__main__':
    data_types()