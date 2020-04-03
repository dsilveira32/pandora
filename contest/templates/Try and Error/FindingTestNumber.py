file = 'shortName_teste_5.py'
file2 = 'shortName_test_5.py'
file3 = 'shortName_5_teste.py'
file4 = 'shortName_5_test.py'
file5 = '5_teste_shortName.py'
file6 = '5_test_shortName.py'
file7 = '5_shortName_teste.py'
file8 = '5_shortName_test.py'

file_ = 'shortName_teste_5.py'
file_2 = 'shortName_test_5.py'
file_3 = 'shortName_5_teste.py'
file_4 = 'shortName_5_test.py'
file_5 = '5_teste_shortName.py'
file_6 = '5_test_shortName.py'
file_7 = '5_shortName_teste.py'
file_8 = '5_shortName_test.py'


def get_test_number(file_parts):
	if len(file_parts) is 2:

		file_name = file_parts[0]

		file_name_parts = file_name.split('_')

		file_name_parts_length = len(file_name_parts)

		if file_name_parts_length > 3:
			return -1
		elif file_name_parts_length is 2:
			try:
				int(file_name_parts[2])
				return file_name_parts[2]
			except ValueError:
				aux = ""
				if 'test' in file_name_parts[1]:
					parts = file_name_parts[1].split('test')

					if '' is parts[0]:
						aux = parts[1] + file_name_parts[2]
					else:
						aux = parts[0] + file_name_parts[2]
				if 'e' in aux:
					file_name_parts = aux.split('e')
					parts = file_name_parts[1].split('e')

					if '' is parts[0]:
						aux = parts[1]
					else:
						aux = parts[0]
				if '_' in aux:
					file_name_parts = aux.split('_')
					parts = file_name_parts[1].split('_')

					if '' is parts[0]:
						aux = parts[1]
					else:
						aux = parts[0]
				return aux
			return file_name_parts[2]
		elif file_name_parts_length is 3:
			try:
				int(file_name_parts[0])
				return file_name_parts[0]
			except ValueError:
				try:
					int(file_name_parts[1])
					return file_name_parts[1]
				except ValueError:
					try:
						int(file_name_parts[2])
						return file_name_parts[2]
					except ValueError:
						return -1

	else:
		return -1

print(get_test_number(file_parts=file.split('.')))
print(get_test_number(file_parts=file2.split('.')))
print(get_test_number(file_parts=file3.split('.')))
print(get_test_number(file_parts=file4.split('.')))
print(get_test_number(file_parts=file5.split('.')))
print(get_test_number(file_parts=file6.split('.')))
print(get_test_number(file_parts=file7.split('.')))
print(get_test_number(file_parts=file8.split('.')))
