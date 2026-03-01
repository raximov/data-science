class Must_Read:
    file_name = "data.csv"
    file = open(file_name, "r")
    file_contents = file.read()
    file.close()
    print(file_contents)

if __name__ == '__main__':
    Must_Read()