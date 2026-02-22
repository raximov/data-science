def read_and_write():
    with open("ds.csv", "r") as f:
        lines = f.readlines()

    result = []
    for line in lines:
        new_line = []
        inside_quotes = False
        for ch in line:
            if ch == '"':
                inside_quotes = not inside_quotes
                new_line.append(ch)
            elif ch == ',' and not inside_quotes:
                new_line.append('\t')
            else:
                new_line.append(ch)
        result.append(''.join(new_line))

    with open("ds.tsv", "w") as f:
        f.writelines(result)


if __name__ == '__main__':
    read_and_write()
