file = 'shortName_teste_5.py'
file2 = 'shortName_test_5.py'
file3 = 'shortName_5_teste.py'
file4 = 'shortName_5_test.py'


def get_test_number(file_parts):
	if len(file_parts) is 2:

		file_name = file_parts[0]

		file_name_parts = file_name.split('_')

		file_name_parts_length = len(file_name_parts)

		if file_name_parts_length > 3:
			return -1
		elif file_name_parts_length is 2:
			return file_name_parts[2]
		elif file_name_parts_length is 3:
			try:
				int(file_name_parts[2])
				return file_name_parts[2]
			except ValueError:
				try:
					int(file_name_parts[1])
					return file_name_parts[1]
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

	else:
		return -1


printer = get_test_number(file_parts=file.split('.'))

print(printer)
print(get_test_number(file_parts=file2.split('.')))
print(get_test_number(file_parts=file3.split('.')))
print(get_test_number(file_parts=file4.split('.')))
