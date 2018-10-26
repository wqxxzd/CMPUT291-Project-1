import sqlite3

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

def check_messages(member):
    #member is a tuple gets the email from tuple
    #using this email we search for inbox that is not seen
    #sets them to seen ('y') UPDATE feature
    
    
    return 0

def login():
    
    while (stop == False):
        print('Menu Options:\n')
        print('l: Login\n')
        print('r: Register\n')
        print('q: Quit\n')
        selection = input()
        if (selection == 'q'):
            return 0
        elif (selection == 'l'):
            #another while loop asking for login info like pw and username
            #If the selected user is valid then stop the while loop
            user = "yes"
        elif (selection == 'r'):
            #Another while loop asking for register info like pw and username
            #Pastes data to the members table (Insert Into)
            #MAKE SURE TO CHECK IF EMAIL GIVEN IS UNIQUE
            user = "yes"
        else:
            print("Syntax error\n")
    return 0

def add_carnumber():
    return 0
    
def add_enroute():
    return 0

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

def offer_ride(driver):
    global connection, cursor    
    
    cursor.execute('SELECT * FROM rides;')
    rides = cursor.fetchall()
    rno = len(rides)     
    
    print("Input date: ")
    date = input()
    print("Input number of seats offered: ")
    seats = input()
    print("Input price per seat: ")
    price = input()
    print("Input luggage description: ")
    lugdesc = input()
    print("Input source location: ")
    src = input()
    src_loc = location_list(src)
    if (src_loc is None):
        print("No location found; return to previous.")
        return 0        
    print("Input destination location: ")
    dst = input()
    dst_loc = location_list(dst)
    if (dst_loc is None):
        print("No location found; return to previous.")
        return 0    
    
    print("Input car number (Blank for null): ")
    cno = input()
    #Checks if car number is valid if not terminates
    
    
    data = (rno,price,date,seats,lugdesc,src_loc[0],dst_loc[0],driver,cno)
    cursor.execute('INSERT INTO rides VALUES (?,?,?,?,?,?,?,?,?)',data)    
    
    while (enstop == False):
        print("Enroutes: \n")
        print("e: Add Enroute\n")
        print("q: Stop Adding Enroute\n")
        s = input()
        if (s == 'e'):
            print("Input destination location: ")
            enloc = input()
            ret_enloc = location_list(enloc)        
            if (ret_enloc is not None):
                #Adds the rno and lcode to the enroute
                lcode = ret_enloc[0]
                rno = rno + 1
                values = (rno, lcode)
                cursor.execute('INSERT INTO enroute VALUES (?,?)',values)
                print("Added enroute\n")
        elif (s == 'q'):
            enstop = True
        else:
            print("Syntax error\n")
    connection.commit()
    return 0

def ride_menu():
    stop = False
    while (stop == False):
        print('Ride Menu:\ns: Stop program\no: Offer rides\n')
        value = input()
        if (value == 's'):
            stop = True
        elif (value == 'o'):
            offer_ride(email)
        else:
            print("Syntax error\n")
    print('Ride menu stopped\n')        
    return 0

def main():
    connect('./test.db')
    login()
    #ride_menu()

main()# Project-1
