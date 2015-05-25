#!/usr/bin/env python
import curses 
import signal
import sys #Handling Ctrl+C
import logging as log
variables=[{}]
screen_list=[0]
pos=1
opcode_list=[{}]
return_to=0
##Logging Level Set
log.basicConfig(level=log.ERROR)

#Curses
stdscr = curses.initscr()
inputs = []
#Key Codes
ENTER=10
TAB=9
ESC=27
SHIFT_TAB=353
BACKSPACE=263
U_BACKSPACE=8 #This is the offical BS key, i think it happens with ^H

curses.noecho()
curses.cbreak()
curses.curs_set(0)
stdscr.keypad(1)

#Quitting Gracefully
def end_program():
	curses.endwin()
	sys.exit(0)

#Open Files
varfile=open("PFL")
code=open("SCN")
# Handle Ctrl+c gracefully
def signal_handler(signal, frame):
	end_program()
signal.signal(signal.SIGINT, signal_handler)


#Populate VarFile
for line in varfile:
	prompt={}
	split = line[0:-1].split(",")
	
	if split[0] == '':
		break
	else:
		prompt["name"]=split[0]
	
	if split[1] != '':
		prompt["type"]=int(split[1])
	else:
		prompt["type"]=0
	
	if split[2] != '':
		prompt["length"]=int(split[2])
	else:
		prompt["length"]=0
	
	if prompt["type"] == 8:
		prompt["value"] = prompt["name"]
	elif prompt["type"] == 4:
			prompt["value"] = 0
	else:
			prompt["value"] = ""
	variables.append(prompt)
#populate Opcode List
for line in code:
	split = line[0:-1].split(",")
	opcode={}
	opcode["command"]=int(split[0])
	if split[1] != "":
		opcode["p1"]=int(split[1])
	else:
		opcode["p1"]=0
	if split[2] != "":
		opcode["p2"]=int(split[2])
	else:
		opcode["p2"]=0
	if split[2] != "":
		opcode["p2"]=int(split[2])
	else:
		opcode["p3"]=0
	if split[3] != "":
		opcode["p3"]=int(split[3])
	else:
		opcode["p3"]=0

	opcode_list.append(opcode)

def update_pos(inputs, usr_pos):
	if usr_pos < 0:
		usr_pos = len(inputs) - 1
	if usr_pos >= len(inputs):
		usr_pos = usr_pos - len(inputs)
	usr_x = inputs[usr_pos]["x"] #Move them to the next
	usr_y = inputs[usr_pos]["y"]
	usr_end = usr_x + inputs[usr_pos]["length"]
	return usr_x, usr_y, usr_end, usr_pos

def edit_form(window=stdscr):
	global pos
	global variables
	global inputs
	log.info(opcode_list[pos])
	while opcode_list[pos]["command"] <= 2000 or opcode_list[pos+1]["command"] == 2999:
		opcode=opcode_list[pos]
		if opcode["command"] == 2999:
			pos=pos+1 
			continue
		log.info("Position is now " + str(pos) + "and the command would be " + str(opcode_list[pos]))
		command = opcode["command"]
		prompt = variables[command]
		p1 = opcode["p1"]
		r = opcode["p2"]
		p2 = opcode["p3"]
		if p1 != 0:
			x_coord=p1%100
			y_coord=p1/100
			stdscr.addstr(y_coord,x_coord, prompt["name"], curses.A_BOLD) #Print the name where it should go
			log.info("Writing " + prompt["name"] + " to " + str(x_coord) + "," + str(y_coord))
		if p2 != 0:
			x_coord=p2%100
			y_coord=p2/100
			if prompt["value"] == "" or prompt["value"] == 0:
				prompt["value"] = r*" "
			stdscr.addnstr(y_coord,x_coord, str(prompt["value"]), r, curses.A_UNDERLINE)
			usr_input = {}
			usr_input["prompt"]=command
			usr_input["x"]=x_coord
			usr_input["y"]=y_coord
			usr_input["length"]=r
			usr_input["type"]=prompt["type"]
			usr_input["value"]=prompt["value"]
			inputs.append(usr_input) ##Keep track of the inputs so we can read them back later
		if pos+1 >= len(opcode_list):
			break
		elif opcode_list[pos+1]["command"] > 2000 and opcode_list[pos+1]["command"] != 2999 :
			break
		else:
			pos=pos+1
		
	#Done creating it, now to deal with user input
	usr_pos = 0
	log.info(inputs)
	usr_x = inputs[usr_pos]["x"] #Start them on the first input area
	usr_y = inputs[usr_pos]["y"]
	usr_end = usr_x + inputs[usr_pos]["length"]
	while True:
		stdscr.chgat(usr_y,usr_x,1,curses.A_REVERSE)
		#log.info("Current position is " + str(usr_x) + "," + str(usr_y))
		ch = stdscr.getch()
		if ch == ENTER: ##Finished Form
			break
		elif ch == curses.KEY_UP:
			stdscr.chgat(usr_y,usr_x,1,curses.A_UNDERLINE)
			usr_pos = usr_pos - 1
			usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
		elif ch == curses.KEY_DOWN:
			stdscr.chgat(usr_y,usr_x,1,curses.A_UNDERLINE)
			usr_pos = usr_pos + 1
			usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
		elif ch == curses.KEY_LEFT:
			stdscr.chgat(usr_y,usr_x,1,curses.A_UNDERLINE)
			usr_x = usr_x - 1
			if usr_x < inputs[usr_pos]["x"]:
				usr_pos = usr_pos - 1
				usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
				usr_x = usr_end - 1
		elif ch == curses.KEY_RIGHT:
			stdscr.chgat(usr_y,usr_x,1,curses.A_UNDERLINE)
			usr_x = usr_x + 1
			if usr_x >= usr_end:
				usr_pos = usr_pos + 1
				usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
			
		elif ch == BACKSPACE or ch == U_BACKSPACE: ##Delete
			if usr_x > inputs[usr_pos]["x"]:
				stdscr.addch(usr_y,usr_x,32,curses.A_UNDERLINE) #Change the old one to underline
				usr_x = usr_x-1
				stdscr.addch(usr_y,usr_x,32)
			else:
				stdscr.addch(usr_y,usr_x,32,curses.A_UNDERLINE) #Change the old one to underline
				usr_pos=usr_pos - 1
				usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
				usr_x = usr_end - 1
				
		elif ch == TAB: ##Next Input
			#Change the old one to underline
			stdscr.chgat(usr_y,usr_x,1,curses.A_UNDERLINE)
			usr_pos = usr_pos + 1
			usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
		elif ch == SHIFT_TAB: #Maybe Shift Tab ( Doesn't work correctly)
			stdscr.chgat(usr_y,usr_x,1,curses.A_UNDERLINE)
			usr_pos = usr_pos - 1
			usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
		else: #They typed something
			if inputs[usr_pos]["type"] == 4:
				if ch >= 48 and ch <= 57: #Valid numbers, 0-9
					stdscr.addch(usr_y,usr_x,ch,curses.A_UNDERLINE) #Change the old one to underline
					usr_x=usr_x+1
					log.info(str(usr_x) + " Is the X, and this is the end " + str(usr_end))
					if usr_x >= usr_end: #Next Input
						log.info("END OF FIELD")
						usr_pos=usr_pos+1
						usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
			elif ch>=32 and ch <=126: #Standard ASCII
				stdscr.addch(usr_y,usr_x,ch,curses.A_UNDERLINE) #Change the old one to underline
				usr_x=usr_x+1
				if usr_x > usr_end: #Next Input
					log.info("END OF FIELD")
					usr_pos=usr_pos+1
					usr_x, usr_y, usr_end, usr_pos = update_pos(inputs, usr_pos)
			else:
				log.info("They hit " + str(ch) )

	#This is where the While Loop ends - all input should be done						
	for usr_input in inputs:
		value=stdscr.instr(usr_input["y"], usr_input["x"], usr_input["length"]).strip() #Read the input
		if value=='':
			if variables[usr_input["prompt"]]["type"] == 4:
				variables[usr_input["prompt"]]["value"]=0
			else:
				variables[usr_input["prompt"]]["value"]=""
		else:
			variables[usr_input["prompt"]]["value"]=value
			log.info("Wrote " + value + " to " + str(usr_input["prompt"]))
	inputs = []
	stdscr.clear()


			
						
				

		
		


		


def arithmatic(cur_val, com_num):
	operation=com_num%10
	number=com_num/10
	if number >= 2200: #Constant
		number=number-2200
		value=number
	else:
		try: value = int(variables[number]["value"])
		except: log.error("The number is " + str(number) + " and the value would be contained in " + str(variables))
	if operation == 1: #Subtraction
		end_val=cur_val - value
	elif operation == 2: #Addition
		end_val=cur_val + value
	elif operation == 3: #Multiplication 
		end_val=cur_val*value
	elif operation == 4: #Division 
		end_val=cur_val/value
	else:
		log.error("NOT A VALID OPERATOR")
		return
	return end_val


def substring_operation(p1, p2, p3):
	prompt_pull=p1/10
	prompt_pos=p2/10 - 1 - 2200
	prompt_len=p3/10  - 2200

	substr=variables[prompt_pull]["value"][prompt_pos:prompt_pos+prompt_len]
	log.info("Substring called for location " + str(prompt_pos) + " to " + str(prompt_pos+prompt_len) + ", returning " + substr)
	return substr
	

def do_math(storage, p1, p2, p3):
	global variables
	value=0
	operation=p1%10
	number=p1/10
	if number >= 2200: #Constant
		number=number-2200
		num_val=number
	else: ##Pull the prompt, put it in the variable
		try: num_val = variables[number]["value"]
		except: 
			log.error("The number is " + str(number) + " and the value would be contained in " + str(variables))
			end_program()

	if operation == 2: #Arithmatic
		value=num_val
	elif operation == 1: #Negative
		value=0-num_val
	elif operation == 0: #Length
		value=variables[number]["length"]
	elif operation == 6: #Substring or power, etc
		p2_op=p2%10
		if p2_op == 5: #Make sure its substring
			value=substring_operation(p1,p2,p3)
			log.info("The variable " + str(storage) + " was changed to " + str(substr) + " on line " + str(pos))
	else:
		log.error("UNKNOWN OPERATION")
	if operation != 6:
		new_val=arithmatic(int(value),int(p2))
		value=arithmatic(int(new_val),int(p3))
	variables[storage]["value"]=value
	log.info("The variable " + str(storage) + " was changed to " + str(value) + " on line " + str(pos))
		


def exec_conditional(p1,cond,p3):
	p1_type=variables[p1]["type"]
	p1_value=variables[p1]["value"]
	if p3 > 20000:
		p3_type=variables[p3-20000]["type"]
		p3_value=variables[p3-20000]["value"]
	elif p3 > 10000 and p3 < 20000:
		p3_type=4
		p3_value=p3-10000
	else:
		log.error("Wrong p3")
	log.info("Comparing " + str(p1_value) + " with " + str(cond) + " to " + str(p3_value))
	if p1_type == 7: # and p3_type !=7: #Special Operation
		log.info("Special Conditional Called")
		log.info(str(p1) + " is type " + str(p1_type))
		if cond == 1: #Null
			if p1_value == 0 or p1_value == "":
				return True
			else:
				return False
		elif cond == 2: #Not Null
			if p1_value != 0 or p1_value != "":
				return
			else:
				return False
		elif cond == 3: #Equal
			if p1_value == p3_value:
				return True
			else:
				return False
		elif cond == 4: #Not Equal
			if p1_value != p3_value:
				return True
			else:
				return False
		else:
			log.error("Unknown operation")
	else:
		if cond == 1: #Less Than
			if p1_value < p3_value:
				return True
			else:
				return False
		elif cond == 2: #Less Than or Equal
			if p1_value <= p3_value:
				return True
			else:
				return False
		elif cond == 3: #Equal
			if p1_value == p3_value:
				return True
			else:
				return False
		elif cond == 4: #Greater Than or Equal
			if p1_value >= p3_value:
				return True
			else:
				return False
		elif cond == 5: #Greater Than
			if p1_value > p3_value:
				return True
			else:
				return False
		elif cond == 6: #Not Equal
			if str(p1_value) != str(p3_value):
				log.info("THIS DIDNT EQUAL THAT")
				return True
			else:
				return False
				log.info("Skipped a position")
		else:
			log.error("Unknown Condition")
		
		
def prompt_text(command, p1,r,p3):
	global variables
	name=variables[command]["name"]
	prevalue = variables[command]["value"] 
	if prevalue == 0:
		value = ""
	else:
		value = prevalue
	if p1 != 0:
		if p3 != 0:
			print name
			val = raw_input(value)
			variables[command]["value"] = val
		else:
			print name
	elif p1 == 0 and p3 != 0:
		log.info(name)
		val = raw_input(value)
		variables[command]["value"] = val
	else:
		log.error("ERRORS")
	
		
	
def goto_page(page_num):
	global pos
	new_pos = screen_list[page_num]
	pos = new_pos
	return

def new_screen(position):
	global screen_list
	screen_list.append(position)

def run_code(opcode):
	global pos 
	global return_to
	command = opcode["command"]
	p1 = opcode["p1"]
	p2 = opcode["p2"]
	p3 = opcode["p3"]
	log.info("Running " + str(opcode))

	if command == 2999: #New Page
		log.debug("Hit new page") ##Maybe I should clear the screen when this happens?
		return ##We already defined pages

	elif command <= 2000: #Display Var
		p1 = p1
		r = p2
		p2 = p3
		#resp = prompt_text(command,p1,r,p2)
		edit_form()
		
	elif command == 3000: #Conditional
		answer=exec_conditional(p1,p2,p3)
		if answer != True:
			pos=pos+1

	elif command == 8500: #Goto
		goto_page(p2)

	elif command >= 10000 and command < 20000: #Storing/Math Operation
		storage=command - 10000
		do_math(storage,p1,p2,p3)

	elif command == 8000: #Create New Page
		log.debug("New Window Created")

	elif command == 3101: #Goto
		if p1 == 0:
			return_to=pos
		else:
			answer=exec_conditional(p1,p2,p3)
			if answer != True:
				pos=return_to
	else:
		log.error("UNKNOWN COMMAND: " + str(command))
			

def define_pages():
	global opcode_list
	for position in range(1, len(opcode_list)):
		if opcode_list[position]["command"] == 2999:
			new_screen(position)
		else:
			continue

def main():
	global pos
	define_pages()
	while True:
		run_code(opcode_list[pos])
		pos=pos+1
		if pos == len(opcode_list):
			break
main()
curses.endwin()

