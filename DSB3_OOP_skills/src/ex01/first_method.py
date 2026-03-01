class Research:

    def file_reader(self):
        file_name = "data.csv"
        file = open(file_name, "r")
        file_contents = file.read()
        file.close()
        return file_contents

    def print_file(self):
        print(self.file_reader())


if __name__ == '__main__':
    read_var = Research()
    read_var.print_file()