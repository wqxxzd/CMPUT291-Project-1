import sqlite3
import datetime
import sys

connection = None
cursor = None

testemail = "bob@123.ca"


def connect(path):
	global connection, cursor
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute(' PRAGMA foreign_keys=ON; ')
	connection.commit()
	return

def tuplestuff(keyword):
	global connection, cursor 
	cursor.execute('SELECT lcode, city, prov, address FROM locations;')
	beforechanges = cursor.fetchall()
	afterchanges = []
	for i in beforechanges:
		if keyword.lower() in i[0].lower():
			afterchanges.append(i)
		elif keyword.lower() in i[1].lower():
			afterchanges.append(i)
		elif keyword.lower() in i[2].lower():
			afterchanges.append(i)
		elif keyword.lower() in i[3].lower():
			afterchanges.append(i)
	return afterchanges
	
def query_to_list(query_statement):
	global connection, cursor
	cursor.execute(query_statement)
	beforechanges = cursor.fetchall()
	afterchanges = []
	for i in beforechanges:
		afterchanges.append(i)
	return afterchanges
	
def list_scrolling(thelist, type_name):
	global connection, cursor
	selected = 0
	v = 0
	if (len(thelist) == 0):
		return None
	print("LIST OF "+ str.upper(type_name) +"(s):\n")
	while (selected == 0):
		for x in range(v, v+5):
			if (x < len(thelist)): 
				print(str(x+1) + ".) " + str(thelist[x]))                
		print("Input number to select "+type_name+";")
		if (v+5 < len(thelist)):
			print("f: Forward")
		if (v != 0):
			print("p: Previous")
		selection = input()
		if (selection == 'f') and (v+5 < len(thelist)):
			v = v + 5
		elif (selection == 'p') and (v != 0):
			v = v - 5
		else:
			try:
				val = int(selection)
				if (val <= len(thelist)):
					selected = val-1
					return selected
				else:
					print("Invalid selection\n")
			except ValueError:
				print("Syntax error\n")      
	return None
	
def Already_Existing(list1, value1, index1):
	for i in range(len(list1)):
		if (list1[i][index1] == value1):
			return True
	return False
	
def Search_For_Rides(user):
	global connection, cursor    
    
	thelist = []
	locations = []
    
	#Also make sure it takes in more than one keyword?
	#As well as some other fixes here and there?
	#Maybe add in car stuff as well?
	stopped = False
	iterate = 1
	while (stopped == False):
		selection = input("How many location keywords (1-3) : ")
		try:
			val = int(selection)
			if (val <= 3 and val >= 1):
				iterate = val
				stopped = True
			else:
				print("Only allow values (1-3)")
		except ValueError:
			print("Syntax error;\n")
	
	for i in range(iterate):
		KEYWORD = input('Input keyword location ' +  str(i+1) + ': ')
		local_locations = tuplestuff(KEYWORD)
		for v in local_locations:
			locations.append(v)
	
	rides = query_to_list('SELECT rno, price, rdate, seats, lugDesc, src, dst, driver, cno FROM rides;')  
	cars = query_to_list('SELECT cno, make, model, year, seats, owner FROM cars;')    

	#Check for all rides that are associated with the given location
	for i in locations:
		for v in rides:
			if ((v[5] == i[0]) or (v[6] == i[0])):
				if (Already_Existing(thelist, v[0], 0)) == False:
					hascar = False
					for b in cars:
						if ((b[0] == v[8]) and (b[5] == v[7])):
							extra_list = v + (b[1], b[2], b[3], b[4])
							
							thelist.append(extra_list)
							hascar = True
					if (hascar == False):
						thelist.append(v)
	selected = list_scrolling(thelist, "ride")
	if selected is not None:
		stop = False
		while (stop == False):
			myinput = input("Send Message? (y/n) : ")
			if myinput == 'y':
				content = input("Enter message: ")
				now = datetime.datetime.now()
				#Is date format correctly done?
				day = str(now.day)
				month = str(now.month)
				if len(day) == 1:
					day = "0"+day
				if len(month) == 1:
					month = "0"+month
				msgTimestamp = str(now.year) + "-" + month + "-" + day
				data = (rides[selected][7],msgTimestamp,user,content,rides[selected][0],'n')
				print(data)
				cursor.execute('INSERT INTO inbox VALUES (?,?,?,?,?,?)',data)    
				connection.commit()
				print("Message successfully sent.\n")
				stop = True
			elif myinput == 'n':
				stop = True
			else:
				print("Incorrect input; Try again.")
	else:
		print("Not selected/No Rides found;")
	return 0

def main():
	print(sys.argv[1])
	connect(sys.argv[1])
	#login()
	Search_For_Rides(testemail)

main()
