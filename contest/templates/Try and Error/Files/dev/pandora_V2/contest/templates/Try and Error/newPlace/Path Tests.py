import os

path = 'main/sec/file.txt'
op = os.path

print("File path: " + op.abspath(path))
print("File directory path: " + op.dirname(path))
print("File name + file type: " + op.basename(path))
