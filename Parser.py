from .AST import AST, List, Num, Op
from .Lexer import Lexer

spec = [('SPACE', '\\ '), 
		('NEWLINE', '\n'),
		('TAB', '\t'), 
		('NUMBER', '[0-9]+'), 
		('LPARA', '('), 
		('RPARA', '\\)'), 
		('NULL_L', r'\(\)'),
		('SUM', '\\+'),
		('CONCAT', '\\+\\+'),
		('LAMBDA', 'lambda\\ +([a-z]|[A-Z])+:'),
		('ID', '([a-z]|[A-Z])+')]

lambda_spec = [('SPACE', '\\ '),
				('NEWLINE', '\n'),
				('TAB', '\t'),
				('EXPR', '\\(*\\ *\\+*\\ *\\(*\\ *(:|[a-z]|[A-Z]|\\ |\\+)+\\ *\\)*\\ '),
				('VALUE', '\\(*\\ *(:|[a-z]|[A-Z]|\\ |\\+|[0-9]|\t|\n)+\\ *\\)*'),
				('RPARA', ')')]

lexer = Lexer(spec)
lambda_lexer = Lexer(lambda_spec)

def parse(tokens: list, root: AST) -> AST:
    # analyze the list of tokens
	while tokens:
		token = tokens.pop(0)
		if token[0] == 'LPARA':
			# determine what the input wants as output
			# and what might be in the expression
			for what in tokens:
				if what[0] == 'NUMBER' or what[0] == 'NULL_L':
					if isinstance(root, List) or isinstance(root, Op):
						child = AST()
						tokens.insert(0, ('LPARA', '('))
						# go deep in the AST
						child = parse(tokens, child)
						root.children.append(child)
					else:
						root = List(token, [])
					break
				elif what[0] == 'SUM' or what[0] == 'CONCAT':
					root = Op(what[0], [])
					child = AST()
					child = parse(tokens, child)
					root.children.append(child)
					break
				elif what[0] == 'LAMBDA':
					# LAMBDA CASE -> eliminate lambdas and return tokens that describes either
					# either a list or a number
					new_tokens = evaluate_lambda(tokens)
					new_tokens.extend(tokens)
					tokens = new_tokens
					if tokens[0][0] == 'LAMBDA':
						tokens.insert(0, ('LPARA', '('))
		elif token[0] == 'RPARA':
			# this is the case where parser reaches the final paranthesis
			# from the input
			return root
		elif token[0] == 'NUMBER':
			# create child
			child = Num(token)
			# case where there is a single lambda and the result is a number
			if not(isinstance(root, Op) or isinstance(root, List)):
				# output should be just a number, not a list
				# so there is an inseration of tokens that makes
				# the sum of a list with the number as the only member
				root = Op('SUM', [])
				child = AST()
				tokens.insert(0, ('SUM', '+'))
				tokens.insert(1, ('LPARA' ,'('))
				tokens.insert(2, token)
				tokens.insert(3, ('RPARA', ')'))
				child = parse(tokens, child)
				root.children.append(child)
			root.children.append(child)
		elif token[0] == 'NULL_L':
			# treat '()' as a Number Node with value 0 for the sum
			child = Num(token)
			root.children.append(child)
	return root

# interpret the AST
def evaluate(root: AST()) -> str:
	output = ''
	if isinstance(root, List):
		output += '( '
		for child in root.children:
			if isinstance(child, Num):
				output += child.value + ' '
			elif isinstance(child, List):
				output += evaluate(child) + ' '
		output += ')'
	elif isinstance(root, Op):
		if root.token == 'SUM':
			# evaluate the sum between the children
			res = evaluate_sum(root.children[0].children)
			if type(res) == int:
				output += str(res)
			else:
				output += res
			return output
		elif root.token == 'CONCAT':
			output += '( '
			for index, elem in enumerate(root.children[0].children):
				if isinstance(elem, Num) and elem.token == 'NULL_L':
					root.children[0].children.pop(index)
			output += evaluate_concat(root.children[0].children)
			output += ')'
	return output

def evaluate_sum(list_s) -> int:
	res = 0
	for child in list_s:
		if isinstance(child, Num):
			if child.value == '()':
				continue
			res += int(child.value)
		elif isinstance(child, List):
			# recursively find the sum of the child and add to the result
			res += evaluate_sum(child.children)
	return res

def evaluate_concat(list_s) -> int:
	output = ''
	for child in list_s:
		if isinstance(child, Num):
			output += child.value + ' '
		elif isinstance(child, List):
			# recursively add the elements of the list to the final list
			output += evaluate_concat(child.children)
	return output

def evaluate_lambda(tokens) -> list:
	left_para = 1
	the_expression = ''
	values = []
	who_to_replace_first = []
	denied_variables = [] # list of elements that will not be replaced by any value
	lambda_inside = False
	already_evaluated = False
	while tokens and left_para:
		# analyze the tokens
		token = tokens.pop(0)
		if token[0] == 'LPARA':
			left_para += 1
		elif token[0] == 'RPARA':
			left_para -= 1
		elif token[0] == 'LAMBDA' and not already_evaluated:
			# take the ID
			ID = token[1][7:len(token[1]) - 1]
			# add to the list of replacements
			who_to_replace_first.append(ID)
			while tokens:
				# see if there are other variables with lambda
				another_lambda = tokens.pop(0)
				if another_lambda[0] == 'LAMBDA':
					ID = another_lambda[1][7:len(token[1]) - 1]
					# check if the ID found has already been added
					if not ID in who_to_replace_first:
						who_to_replace_first.append(ID)
					else:
						tokens.insert(0, another_lambda)
						lambda_inside = True
						break
				elif another_lambda[0] == 'SPACE':
					continue
				else:
					tokens.insert(0, another_lambda)
					break
			# get the values and the expression on which there will be replacements
			(values, the_expression, denied_variables) = get_values_and_expr(tokens)
			# case where there is already a certain lambda
			if lambda_inside:
				tokens.pop(0)
				lambda_inside = False
			# evaluation of the main lambda expression is over
			already_evaluated = True
	replacers = {} # a dictionary where the key is the variable and the value is
				   # what will it be
	while who_to_replace_first:
		first_variable = who_to_replace_first.pop(0)
		first_value = values.pop(0)
		# eliminate any character that does not relate to the objective
		first_value = first_value.replace('\n', '')
		first_value = first_value.replace('\t', '')
		if not first_variable in denied_variables:
			replacers[first_variable] = first_value
	# build the expression with the replacements made
	new_expression = ''
	for char in the_expression:
		if char in replacers:
			new_expression += replacers[char]
		else:
			new_expression += char
	# add the remaining values left that will be used later
	while values:
		new_expression += values.pop(0) + ')'
	# get the new tokens
	lambda_res = lexer.lex(new_expression)
	for what in lambda_res:
		# check if the new expression has lambda in it
		# if so, there will be a new evaluation of the new lambda expression
		if what[0] == 'LAMBDA':
			lambda_res = evaluate_lambda(lambda_res)
	return lambda_res
		
# get the values and the expression
def get_values_and_expr(tokens: list) -> (list, str, list):
	expression = ''
	values = []
	denied_variables = []
	had_lambda_inside = False
	# build the expression that is being analyzed
	for token in tokens:
		expression += token[1]
	# get the lambda tokens
	lambda_res = lambda_lexer.lex(expression)
	expression = ''
	for index, token in enumerate(lambda_res):
		# case where the token has the expression and the value and it is being seen as a value
		# first token is the expression
		if token[0] == 'VALUE' and index == 0:
			# eliminate useless characters
			revised = token[1].replace('\n', '')
			revised = revised.replace('\t', '')
			special_case = revised.split(' ')
			index = 0
			# get the expression
			while index < len(special_case) - 1:
				if index == len(special_case) - 2:
					expression += special_case[index]
				else:
					expression += special_case[index] + ' '
				index += 1
			# get the value
			value = special_case[len(special_case) - 1]
			# if the value is a list
			l_para = 0
			r_para = 0
			for char in value:
				if char == '(':
					l_para += 1
				elif char == ')':
					r_para += 1
			# eliminate any right paranthesis that are not in the value
			while l_para != r_para:
				value = value[:len(value) - 1]
				r_para -= 1
			# add the value
			values.append(value)
			# add the variable that will not be replaced since it is already part of a value
			denied_variables.append(special_case[1][:len(special_case[1]) - 1])
			continue
		if token[0] == 'VALUE':
			if had_lambda_inside:
				denied_variables.append(token[1].replace(')', ''))
				had_lambda_inside = False
				continue
			value = token[1]
			l_para = 0
			r_para = 0
			for char in value:
				if char == '(':
					l_para += 1
				elif char == ')':
					r_para += 1
			while l_para != r_para:
				value = value[:len(value) - 1]
				r_para -= 1
			values.append(value)
		elif token[0] == 'EXPR':
			# if there is already the expression
			# it means that any expression is actually a value
			if expression != '':
				value = token[1]
				l_para = 0
				r_para = 0
				for char in value:
					if char == '(':
						l_para += 1
					elif char == ')':
						r_para += 1
				while l_para != r_para:
					value = value[:len(value) - 1]
					r_para -= 1
				values.append(value.replace(')', ''))
				continue
			if 'lambda' in token[1]:
				modify_token = token[1].split(' ')
				if modify_token[0] != 'lambda':
					while modify_token:
						m_tok = modify_token.pop(0)
						# if there is lambda expression, it means that is a value
						# and not part of the expression
						if m_tok == 'lambda':
							# build the lambda value
							new_new_token = m_tok + ' '
							for i, elem in enumerate(modify_token):
								if i == len(modify_token) - 1:
									new_new_token += elem
								else:
									new_new_token += elem + ' '
							value = new_new_token
							l_para = 0
							r_para = 0
							for char in value:
								if char == '(':
									l_para += 1
								elif char == ')':
									r_para += 1
							while l_para != r_para:
								value = value[:len(value) - 1]
								r_para -= 1
							# append the lambda value to the values
							values.append(value.replace(')', ''))            
							break
						else:
							# add the part to the expression
							expression += m_tok
					continue
				had_lambda_inside = True
			else:
				# take the expression
				expression = token[1]
				# if this is the beginning and the next tokens are an expression
				# add it to the final expression
				if index == 0:
					while lambda_res:
						new_token = lambda_res.pop(1)
						if new_token[0] == 'EXPR':
							expression += new_token[1]
						else:
							lambda_res.insert(1, new_token)
							break
	return (values, expression, denied_variables)

def print_result(filename: str):
	expression = ''
	with open(filename, 'r') as file:
		# Read the contents of the file into a string
		expression = file.read()
	tokens = lexer.lex(expression)
	root = parse(tokens, AST())
	res = evaluate(root)
	print(res)