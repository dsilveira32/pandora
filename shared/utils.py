# ------------------------------------------------------- debug -------------------------------------------------------
# forms
def print_form_info_debug(form):
	if not form.is_valid():
		print("-----------------------------------\nThe form is built with:\n" + str(form) +
			  "\n-----------------------------------")
	print("-----------------------------------\nThe form is valid: " + str(form.is_valid()) +
		  "\n-----------------------------------")

	return


# variable
def print_variable_debug(variable):
	print("-----------------------------------------------------------------\n"
		  + str(variable) +
		  "\n-----------------------------------------------------------------")

	return


# variables
def print_variables_debug(variables):
	variable_debug = ''
	for part in variables:
		if variable_debug == '':
			variable_debug = str(part)
		else:
			variable_debug += '\n' + str(part)
	print_variable_debug(variable_debug)

	return