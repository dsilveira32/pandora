import os

path = '/home/bruno/dev/pandora/contest/templates/Try and Error/Files/1234.zip'

print("\nFile path: " + path)

count = 0

for c in os.walk(os.path.dirname(path)):
	print(c)
	count += 1

pos = 0

print("start")

for file in os.walk(os.path.dirname(path)):
	print("searching in " + str(file))
	newFolder = str(file[0]) + "/newPlace"
	pos += 1
	if pos == count:
		print(str(file[len(file) - 1]) + "\n\n")
		for f in file[len(file) - 1]:
			print(f)
			f_parts = f.split('.')
			print(f_parts[len(f_parts) - 1])

			if not os.path.isdir(newFolder):
				os.mkdir(newFolder)
			os.replace(str(file[0]) + "/" + str(f), str(file[0]) + "/newPlace/" + str(f))
