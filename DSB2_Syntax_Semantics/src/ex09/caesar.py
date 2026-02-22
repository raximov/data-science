import sys


def caesar():
    if len(sys.argv) != 4:
        raise Exception("Wrong number of arguments")

    mode = sys.argv[1]
    text = sys.argv[2]
    shift = int(sys.argv[3])

    if mode not in ('encode', 'decode'):
        raise Exception("First argument must be 'encode' or 'decode'")

    for ch in text:
        if '\u0400' <= ch <= '\u04FF' or '\u0500' <= ch <= '\u052F':
            raise Exception("The script does not support your language yet.")

    if mode == 'decode':
        shift = -shift

    result = []
    for ch in text:
        if ch.isalpha() and ch.isascii():
            if ch.islower():
                base = ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
            else:
                base = ord('A')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)

    print(''.join(result))


if __name__ == '__main__':
    caesar()
