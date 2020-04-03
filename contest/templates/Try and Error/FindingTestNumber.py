files = [
	# size 3
	'shortName_teste_5.py',
	'shortName_test_5.py',

	'teste_shortName_5.py',
	'test_shortName_5.py',

	'shortName_5_teste.py',
	'shortName_5_test.py',

	'teste_5_shortName.py',
	'test_5_shortName.py',

	'5_teste_shortName.py',
	'5_test_shortName.py',

	'5_shortName_teste.py',
	'5_shortName_test.py',

	# size 2
	'shortName_teste5.py',
	'shortName_test5.py',

	'teste5_shortName.py',
	'test5_shortName.py',

	'shortName_5teste.py',
	'shortName_5test.py',

	'5teste_shortName.py',
	'5test_shortName.py',

	'shortNameteste_5.py',
	'shortNametest_5.py',

	'5_shortNameteste.py',
	'5_shortNametest.py',

	'testeshortName_5.py',
	'testshortName_5.py',

	'5_testeshortName.py',
	'5_testshortName.py',

	'teste_shortname5.py',
	'test_shortname5.py',

	'shortname5_teste.py',
	'shortname5_test.py',

	'teste_5shortname.py',
	'test_5shortname.py',

	'5shortname_teste.py',
	'5shortname_test.py',

	# size 1
	'shortnameteste5.py',
	'shortnametest5.py',

	'shortname5teste.py',
	'shortname5test.py',

	'testeshortname5.py',
	'testshortname5.py',

	'teste5shortname.py',
	'test5shortname.py',

	'5shortnameteste.py',
	'5shortnametest.py',

	'5testeshortname.py',
	'5testshortname.py',

	# without the word test
	'5shortname.py',
	'5shortname.py',

	'shortname5.py',
	'shortname5.py',

	'5_shortname.py',
	'5_shortname.py',

	'shortname_5.py',
	'shortname_5.py',

]


def get_test_number(file_parts, short_name):

	short_name = short_name.lower()

	file_parts_aux = file_parts

	for i in range(len(file_parts_aux)):
		file_parts[i] = file_parts_aux[i].lower()

	if len(file_parts) is 2:

		file_name = file_parts[0]

		file_name_parts = file_name.split('_')

		file_name_parts_length = len(file_name_parts)

		if file_name_parts_length > 3:
			return -1
		elif file_name_parts_length is 1:
			parts = file_name_parts[0].split(short_name)
			try:
				int(parts[0])
				return parts[0]
			except ValueError:
				try:
					int(parts[1])
					return parts[1]
				except ValueError:
					if '' is parts[0]:
						aux = str(parts[1])
					else:
						aux = str(parts[0])
					if 'test' in aux:
						parts = aux.split('test')

						if '' is parts[0]:
							aux = parts[1]
						else:
							aux = parts[0]
					if 'e' in aux:
						parts = aux.split('e')

						if '' is parts[0]:
							aux = parts[1]
						else:
							aux = parts[0]
					return aux

		elif file_name_parts_length is 2:
			try:
				int(file_name_parts[0])
				return file_name_parts[0]
			except ValueError:
				try:
					int(file_name_parts[1])
					return file_name_parts[1]
				except ValueError:
					parts = []
					if short_name in file_name_parts[1]:
						parts = file_name_parts[1].split(short_name)
						if str(parts[0]) is str(parts[1]) is '':
							aux = ""
							if 'test' in file_name_parts[0]:
								parts = file_name_parts[0].split('test')
								if '' is parts[0]:
									aux = str(parts[1])
								else:
									aux = parts[0]
							if 'e' in aux:
								parts = aux.split('e')

								if '' is parts[0]:
									aux = parts[1]
								else:
									aux = parts[0]
							return aux
						elif str(parts[0]) is not '':
							return parts[0]
						elif str(parts[1]) is not '':
							return parts[1]
					elif short_name in file_name_parts[0]:
						parts = file_name_parts[0].split(short_name)
						if str(parts[0]) is str(parts[1]) is '':
							aux = ""
							if 'test' in file_name_parts[1]:
								parts = file_name_parts[1].split('test')
								if '' is parts[0]:
									aux = str(parts[1])
								else:
									aux = parts[0]
							if 'e' in aux:
								parts = aux.split('e')
								if '' is parts[0]:
									aux = parts[1]
								else:
									aux = parts[0]
							return aux
						elif str(parts[0]) is not '':
							return parts[0]
						elif str(parts[1]) is not '':
							return parts[1]
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


for file in files:
	print(str(file) + " -> " + str(get_test_number(file.split('.'), "shortName")))
