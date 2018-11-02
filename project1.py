import sqlite3
import datetime
#Testing comments WE$L#$Y{%$H
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
	
def location_list(keyword):
    global connection, cursor
    selected = 0
    v = 0
    loc_list = []
    loc_list = tuplestuff(keyword)
    if (len(loc_list) == 0):
        return None
    #Locations into a list and call it loc_list
    print("LIST OF LOCATIONS:\n")
    while (selected == 0):
        for x in range(v, v+5):
            if (x < len(loc_list)): 
                print(str(x+1) + ".) " + str(loc_list[x]))                
        print("Input number to select location;")
        if (v+5 < len(loc_list)):
            print("f: Forward")
        if (v != 0):
            print("p: Previous")
        selection = input()
        if (selection == 'f') and (v+5 < len(loc_list)):
            v = v + 5
        elif (selection == 'p') and (v != 0):
            v = v - 5
        else:
            try:
                val = int(selection)
                if (val < len(loc_list)):
                    selected = val
                    return loc_list[selected]
            except ValueError:
                print("Syntax error\n")      
    return None
	
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
                if (val < len(thelist)):
                    selected = val
                    return thelist[selected]
            except ValueError:
                print("Syntax error\n")      
    return None
	
def Already_Existing(list1, list2, index1, index2):
    for i in range(len(list1)):
	        for v in range(len(list2)):
                if (list1[i][index1] == list2[v][index2]):
                    return True
	return False
	
def Search_For_Rides(user):
    global connection, cursor    
    
	thelist = []
    rides = query_to_list('SELECT rno, price, rdate, seats, lugDesc, src, dst, driver, cno FROM rides;')  
    cars = query_to_list('SELECT cno, make, model, year, seats, owner FROM cars;')
    print("Input keyword location: ")
	#Also make sure it takes in more than one keyword?
	#As well as some other fixes here and there?
	#Maybe add in car stuff as well?
    keyword = input()
    locations = tuplestuff(keyword)
	#Check for all rides that are associated with the given location
	for i in locations:
	    for v in rides:
		    if ((v[5] == i[0]) or (v[6] == i[0])):
			    if (Already_Existing(thelist, rides, 0, 0)):
				    thelist.append(v)

	selected = list_scrolling(thelist, "ride")
    if selected is not None:
		stop = False
		while (stop == False):
			print("Send Message? (y/n) : ")
			myinput = input()
			if myinput == 'y':
				print("Enter message: ")
				content = input()
				now = datetime.datetime.now()
				#Is date format correctly done?
				msgTimestamp = now.year + "-" + now.month + "-" + now.day
				data = (rides[selected][7],msgTimestamp,user,content,rides[selected][0],'n')
				cursor.execute('INSERT INTO inbox VALUES (?,?,?,?,?,?,?,?,?)',data)    
				cursor.commit()
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
    connect('./test.db')
    login()
    Search_For_Rides(testemail)

main()# Project-1
