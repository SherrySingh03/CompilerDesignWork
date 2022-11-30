'''
main():
This is the primary module that is executed at first. Here user to asked to enter the string to be parsed and also all the feedback 
(like: grammar rules, goto operations, generated states, reduction rules and parse table) are provided to user. 
Final result about if the string is successfully parsed or not, is also printed here.

read_grammar():
This function asks user to provide file name where grammar are stored. It reads the file for grammar and place it on list grammar. 
From the rules terminals and nonterminals are identified and stored in the lists named terminals and non_terminals respectively, 
where as rules are stored in the dictionary called rule_dict.

augmented_grammar():
Using the grammar list created in read_grammar(), it generates list of augmented grammar and place it on new_grammar.

compute_I0():
Here I0 is calculated separately using the rule 1 in new_grammar. The calculated I0 is stored in dictionary I_n with key as 0. 
So the dictionary I_n[0] represents state I0.

GOTO():
Now as I0 state is found, using this initial state I_n[0] further states are generated recursively until all the non repeated valid states of 
the given grammar is generated and stored in the dictionary I_n with their respective state as key. While generating all the state the list 
shift_list keeps track of all the shift operation that are valid for the given grammar.

follow(var):
This generates the follow of nonterminal var and returns it.

reduction():
Here all the possible reduction rules for the given grammar are calculated and stored in the list named reduction_list. 
Each item of reduction_list is another list whose first and second element gives reduction condition and third provides 
the rule to be used for for that condition.

Conflict():
Here, availability of conflict in the given grammar is analyzed. Stores each SR conflict in list SR and RR conflict in list RR. 
It returns True if there is conflict else False.

test(string):
Using reduction_list and shift_list, action_list is created which resembles the SLR parse table. 
Now with the help of action_list, stack and string the parsing is done, while displaying each step and content of stack, 
string and current action thats been called. If the string is acceptable it returns 1 and if not accepted returns 0.

'''

import copy

grammar = []
new_grammar = []
terminals = []
non_terminals = []
I_n = {}
shift_list = []
reduction_list = []
action_list = []
rule_dict = {}
follow_dict = {}
SR = []
RR = []

def Conflict():
	global SR, RR, shift_list, reduction_list
	conflict = False
	# SR conflict if shift and Reduce occurs for same condition
	for S in shift_list:
		for R in reduction_list:
			if S[:2] == R[:2]:
				SR.append([S, R])
				conflict = True

	# RR conflict if 2 Reduce occurs for same condition
	for R1 in reduction_list:
		for R2 in reduction_list:
			if R1 == R2:
				continue

			if R1[:2] == R2[:2]:
				RR.append(R1)
				conflict = True

	return conflict


def read_grammar():
	global grammar, terminals, non_terminals, rule_dict

	file_name = input("Enter Grammar File Name:: ")

	# open given file
	try:
		grammar_file = open(file_name, "r")
	except:
		print("Cannot Find File Named", file_name)
		exit(0)

	# add grammar
	for each_grammar in grammar_file:
		grammar.append(each_grammar.strip())

		# find terminals
		if each_grammar[0] not in non_terminals:
			non_terminals.append(each_grammar[0])

	# find non terminals
	for each_grammar in grammar:
		for token in each_grammar.strip().replace(" ", "").replace("->", ""):
			if token not in non_terminals and token not in terminals:
				terminals.append(token)

	# generate dictionary of rules
	for l in range(1, len(grammar)+1):
		rule_dict[l] = grammar[l-1]


def augmented_grammar():
	global grammar, new_grammar
	read_grammar()

	# if non augmented grammar is given, augment it
	if "'" not in grammar[0]:
		grammar.insert(0, grammar[0][0]+"'"+"->"+grammar[0][0])

	# just add . infornt of each rule
	new_grammar = []
	for each_grammar in grammar:
		idx = each_grammar.index(">")

		each_grammar = each_grammar[:idx+1]+"."+each_grammar[idx+1:]
		new_grammar.append(each_grammar)



def compute_I0():
	global new_grammar, non_terminals, I_n
	augmented_grammar()

	grammar2add = []

	grammar2add.append(new_grammar[0])
	i = 0

	for each in grammar2add:
		current_pos = each.index(".")
		current_variable = each[current_pos+1]

		if current_variable in non_terminals:
			for each_grammar in new_grammar:
				if each_grammar[0] == current_variable and each_grammar not in grammar2add:
					grammar2add.append(each_grammar)

		I_n[i] = grammar2add


def GOTO():
	global grammar, non_terminals, terminals, I_n, shift_list
	compute_I0()

	variables = non_terminals + terminals
	# variables = ["E", "T", "F", "(", ")", "+", "*", "i"]

	# I_n[0]
	i = 0
	current_state = 0
	done = False
	
	while (not done):
		for each_variable in variables:
			grammar2add = []

			try:
				for each_rule in I_n[current_state]:
					if each_rule[-1] == ".":
								continue
					dot_idx = each_rule.index(".")

					if each_rule[dot_idx+1] == each_variable:
						
						rule = copy.deepcopy(each_rule)
						rule = rule.replace(".", "")
						rule = rule[:dot_idx+1]+"."+rule[dot_idx+1:]
						grammar2add.append(rule)

						for rule in grammar2add:
							dot_idx = rule.index(".")
							if rule[-1] == ".":
								pass
							else:
								current_variable = rule[dot_idx+1]
								
								if current_variable in non_terminals:
									for each_grammar in new_grammar:
										if each_grammar[0] == current_variable and each_grammar[1] != "'" and each_grammar not in grammar2add:
											grammar2add.append(each_grammar)

			except:
				done = True
				break

			if grammar2add:

				if grammar2add not in I_n.values():
					i += 1
					I_n[i] = grammar2add

				for k,v in I_n.items():
					if grammar2add == v:
						idx = k
				
				shift_list.append([current_state, each_variable, idx])
					
		current_state += 1


def follow(var):
	
	global rule_dict, follow_dict, terminals

	value = []
	if var == rule_dict[1][0]:
		value.append("$")

	for rule in rule_dict.values():
		
		lhs, rhs = rule.split("->")

		if var == rule[-1]:
			for each in follow(rule[0]):
				if each not in value:
					value.append(each)

		if var in rhs:
			idx = rhs.index(var)

			try:
				if rhs[idx+1] in non_terminals and rhs[idx+1] != var:
					for each in follow(rhs[idx+1]):
						value.append(each)
						# print "AAAA", var
				else:
					value.append(rhs[idx+1])
			except:
				pass
	

	return value


def reduction():
	global I_n, rule_dict, reduction_list
	
	reduction_list.append([1, "$", "Accept"])

	for item in I_n.items():
		try:
			for each_production in item[1]:
				lhs, rhs = each_production.split(".")

				for rule in rule_dict.items():

					if lhs == rule[1]:
						f = follow(lhs[0])

						for each_var in f:
							reduction_list.append([item[0], each_var, "R"+str(rule[0])])

		except:
			# print item
			pass





def main():
	global I_n, shift_list, reduction_list, action_list, SR, RR

	GOTO()
	reduction()



	print("\n--------------------RULES--------------------")
	for item in rule_dict.items():
		print (item)


	print ("\n--------------------AUGMENTED RULES--------------------")
	for item in new_grammar:
		print (item.replace(".", ""))

	print ("\n--------------------STATES--------------------")
	for item in I_n.items():
		print (item)


	print ("\n--------------------GOTO OPERATIONS--------------------")
	for item in shift_list:
		print (item)


	print ("\n--------------------REDUCTION--------------------")
	for item in reduction_list:
		print (item)

	if Conflict():
		if SR != []:
			print ("SR conflict")
			for item in SR:
				print (item)
			print(" ")

		if RR != []:
			print ("RR conflict")
			for item in RR:
				print (item)
			print

		exit(0)
	else:
		print ("\nNO CONFLICT\n")

	print ("Terminals:", terminals)
	print ("NonTerminals:", non_terminals)
	print
			
	action_list.extend(shift_list)
	action_list.extend(reduction_list)


	return 0



if __name__ == '__main__':
	main()
