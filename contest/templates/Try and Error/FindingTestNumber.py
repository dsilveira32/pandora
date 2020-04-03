file = 'shortName_teste_Number.py'
file2 = 'shortName_test_Number.py'
file3 = 'shortName_Number_teste.py'
file4 = 'shortName_Number_test.py'


def get_number(file_parts):
	if len(file_parts) is 2:

		file_name = file_parts[0]

		file_name_parts = file_name.split('_')

		file_name_parts_length = len(file_name_parts)

		if file_name_parts_length > 3:
			print(False)
		elif file_name_parts_length is 3:
			print(file_name_parts[2])
		elif file_name_parts_length is 2:
			try:
				int(file_name_parts[1])
			except ValueError:
				number = 0
				aux = ""
				if 'test' in file_name_parts[1]:
					parts = file_name_parts[1].split('test')

					if 'test' is parts[0]:
						aux = parts[1]
					else:
						aux = parts[0]
				if 'e' in file_name_parts[1]:
					parts = file_name_parts[1].split('e')

					if 'e' is parts[0]:
						aux = parts[1]
					else:
						aux = parts[0]
				if '_' in file_name_parts[1]:
					parts = file_name_parts[1].split('_')

					if '_' is parts[0]:
						aux = parts[1]
					else:
						aux = parts[0]
				print(aux)

	else:
		print(False)


get_number(file_parts=file.split('.'))
get_number(file_parts=file2.split('.'))
get_number(file_parts=file3.split('.'))
get_number(file_parts=file4.split('.'))
