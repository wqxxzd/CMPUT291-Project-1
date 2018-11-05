import sqlite3
import re
import getpass
import sys

connection = None
cursor = None


def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return 0



def DisplayScript(script):
    global connection, cursor
    cursor.execute(script)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        print("\n")
    return 0



def checklocations(lcode):
    global connection, cursor
    l = []
    data = (lcode,)
    cursor.execute('SELECT lcode FROM locations WHERE lcode = ?;', data)
    l = cursor.fetchall()
    if not l:
        return False
    else:
        return True



def PostRideRequests(current_email):
    #The member should be able to post a ride request by providing a date, a pick up location code, a drop off location code, and the amount willing to pay per seat. 
    
    #The request rid is set by your system to a unique number and the email is set to the email address of the member.
    
    #Assume the user input in the correct format 
    
    global connection, cursor
    
    #Ask for the date and check the format
    valid = False
    while (valid == False):
        rdate = input('Please provide a date (Year-Month-Date): ')
        #https://stackoverflow.com/questions/22061723/regex-date-validation-for-yyyy-mm-dd
        if(re.match('^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$', rdate)):
            valid = True
        else:
            print('Invalid format, please try again.')
    
    #Ask for the pickup location
    valid = False
    while (valid == False):
        pickup = input('Please provide a pick up location code: ')
        if (checklocations(pickup)):
            valid = True
        else:
            print('Pick up location DNE, please try again')
            
    #Ask for the dropoff location
    valid = False
    while (valid == False):
        dropoff = input('Please provide a drop off location code: ')
        if (checklocations(dropoff)):
            valid = True
        else:
            print('Drop off location DNE')
    
    #ASk for the the amount willing to pay per seat
    amount = input('Please provide the amount willing to pay per seat: ')
    
    cursor.execute('SELECT MAX(rid) FROM requests')
    maxrid = cursor.fetchall()
    if not maxrid:#If the list is empty
        rid = 1
    else:
        rid = maxrid[0][0] + 1
    data = (rid, current_email, rdate, pickup, dropoff, amount)
    cursor.execute('INSERT INTO requests VALUES (?,?,?,?,?,?);',data)
    
    connection.commit()
    return 0



def DeleteRideRequests():
    global connection, cursor
    valid = False
    while(valid == False):
        rid = input('Please enter the rid that you want to delete: ')
        data = (rid,)
        cursor.execute('SELECT * FROM requests WHERE rid = ?;',data)
        rows = cursor.fetchall()
        if not rows:
            print('Please choos a valid rid.')
        else:
            cursor.execute('DELETE FROM requests WHERE rid = ?;',data)
            valid = True
    connection.commit()
    return 0



def DisplayRideRequests(current_email):
    #The member should be able to see all his/her ride requests and be able to delete any of them.
    global connection, cursor
    data = (current_email,)
    cursor.execute('SELECT * FROM requests WHERE email = ?;',data)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        
    valid = False
    while(valid == False):
        print('--------------------------------------------------')
        print('Insert a request: i\nDelete a request: d\nGo back: g')
        print('--------------------------------------------------')
        key = input('Please make a selection: ')
        if (key == 'i'):
            valid = True
            PostRideRequests(current_email)
        elif (key == 'd'):
            valid = True
            DeleteRideRequests()
        elif (key == 'g'):
            return 0
        else:
            print('Invalid option. please try again.')
    return 0



def KeywordToList(keyword): 
    global connection, cursor 
    
    cursor.execute('SELECT rid, email, rdate, pickup, dropoff, amount FROM requests;')
    beforechanges = cursor.fetchall()
    afterchanges = []
    for i in beforechanges:
        if keyword.lower() == i[3].lower():
            afterchanges.append(i)
    if not afterchanges:
        cursor.execute('SELECT lcode,city FROM locations;')
        citylist = cursor.fetchall()
        for lcodecity in citylist:
            #print(lcodecity[1])
            if keyword.lower() == lcodecity[1].lower():
                newkey = lcodecity[0]
                #print(newkey)
                for i in beforechanges:
                    if newkey.lower() == i[3].lower():
                        afterchanges.append(i)
    return afterchanges    



def DisplayLocationList():
    global connection, cursor
    selected = 0
    v = 0
    loc_list = []
    valid = False
    while (valid == False):
        keyword = input('Please enter a location code/city: ')
        loc_list = KeywordToList(keyword)
        if (len(loc_list) != 0):
            valid = True
        else:
            print('Invalid location code/city, please try again')
    #Locations into a list and call it loc_list
    print("LIST OF LOCATIONS:\n")
    while (selected == 0):
        for x in range(v, v+5):
            if (x < len(loc_list)): 
                print(str(x+1) + ".) " + str(loc_list[x]))                
        print("\nSelect a location and message the posting member:")
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
                if (val < len(loc_list)+1):
                    selected = val -1
                    return loc_list[selected]
            except ValueError:
                print("Syntax error\n")      
    return None



def SendAMessage(fromemail, toemail):
    global connection, cursor
    content = input('Please input the content of your message: ')
    cursor.execute('''SELECT datetime('now', 'localtime');''')
    time = cursor.fetchall()
    valid = False
    while(valid == False):
        rno = input('Please enter the rno of the regarding ride: ')
        data = (rno, )
        cursor.execute('SELECT rno FROM rides WHERE rno = ?', data)
        rnolist = cursor.fetchall()
        if not rnolist:
            print('Invalid rno, please check and enter again.')
        else:
            valid = True
    data = (toemail, time[0][0], fromemail, content, rno, 'n')
    cursor.execute('INSERT INTO inbox VALUES (?,?,?,?,?,?);',data)
    print('Message Sent.')
    connection.commit()
    return 0



def SearchaDeleteRideRequests(current_email):
    #The member should be able to see all his/her ride requests and be able to delete any of them.
    
    #Also the member should be able to provide a location code or a city and see a listing of all requests with a pickup location matching the location code or the city entered.If there are more than 5 matches, at most 5 matches will be shown at a time. 
    
    #The member should be able to select a request and message the posting member, for example asing the member to check out a ride.   

    global connection, cursor
    
    while (1):
        print('--------------------------------------------------')
        print('|       [Search and delete ride requests]        |')
        print('|                                                |')
        print('|            See all ride requests: r            |')
        print('|   See all requests with a pickup location: p   |')
        print('|                Return to home: h               |')
        print('--------------------------------------------------')
        sel = input('Please make a selection: ')
        if (sel.lower() == 'r'):
            print('\nAll ride requests:')
            DisplayRideRequests(current_email)
        elif (sel.lower() == 'p'):
            print('\nAll requests with a pickup location:')
            sel = DisplayLocationList()
            SendAMessage(current_email, sel[1])
            #sel is a tuple with info: rid|email|rdate|pickup|dropoff|amount
            print(sel)
        elif (sel.lower() == 'h'):
            return 0
        else:
            print('Invalid selection, please check the menu again.')
            
    connection.commit()
    return 0



def Login():
    #Existing members should be able to login using a valid email and password, denoted with email and pwd in table members. After a login, all unseen messages of the member will be displayed, and the status of the messages will be set to seen (i.e, the seen column is set to 'y'). 
    global connection, cursor
    
    valid = False
    while(valid == False):
        email = input('Please enter the email: ')
        pwd = getpass.getpass('Please enter the password:')
        data = (pwd,)
        cursor.execute('SELECT email FROM members WHERE pwd = ?;', data)
        emaillist = cursor.fetchall()
        match = False
        for e in emaillist:
            if (match == False):
                if (email.lower() == e[0].lower()):
                    match = True
        if (match == False):
            print('Email address does not exisist/password does not match, please try again')
        else:
            valid = True
    data = (email, )
    cursor.execute('''SELECT msgTimestamp, sender, content FROM inbox WHERE email = ? AND seen = 'n';''', data)
    msglist = cursor.fetchall()
    print('\n')
    if not msglist:
        print('No new message.')
    else:
        print('The following is all unread message:')
        for m in msglist:
            print(m)
    cursor.execute('''UPDATE inbox SET seen = 'y' WHERE seen = 'n' AND email = ?;''', data)
    connection.commit()
    return email



def NewUser():
    #Unregistered members should be able to sign up by providing a unique email, a name, a phone, and a password. Proper messages should be given if the provided email is not unique. After a successful login or signup, members should be able to perform the subsequent operations (possibly chosen from a menu) as discussed next.
    global connection, cursor
    
    email = input('Please enter your email: ')
    name = input('Please enter your name: ')
    phone = input('Please enter your phone:')
    pwd = getpass.getpass('Please enter your password:')
    data = (email, name, phone, pwd)
    cursor.execute('INSERT INTO members values (?,?,?,?);', data)
    connection.commit()
    return email



def LoginOrRegister():
    #The first screen of your system should provide options for members to login and for new members to register. Existing members should be able to login using a valid email and password, denoted with email and pwd in table members. After a login, all unseen messages of the member will be displayed, and the status of the messages will be set to seen (i.e, the seen column is set to 'y'). Unregistered members should be able to sign up by providing a unique email, a name, a phone, and a password. Proper messages should be given if the provided email is not unique. After a successful login or signup, members should be able to perform the subsequent operations (possibly chosen from a menu) as discussed next.

    #Members should be able to logout and there must be also an option to exit the program.
    global connection
    
    valid = False
    while (valid == False):
        print('-------------------------')
        print('|       [Welcome]       |')
        print('|                       |')
        print('|       Log In: l       |')
        print('|      Register: r      |')
        print('|        Exit: e        |')
        print('-------------------------')
        key = input('Please select: ')
        if(key.lower() == 'l'):
            valid = True
            email = Login()
        elif(key.lower() == 'r'):
            valid = True
            email = NewUser()
        elif(key.lower() == 'e' ):
            connection.close()             
            sys.exit(0)
        else:
            print('Invalid option, please try again.')  
    return email
    
    
    
def DisplayMenu():
    print('--------------------------------------------------')
    print('|                  [HOME MENU]                   |')
    print('|                                                |')
    print('|                Offer a ride: o                 |')
    print('|              Search for rides: s               |')
    print('|       Book members or cancel bookings: b       |')
    print('|             Post ride requests: p              |')
    print('|       Search and delete ride requests: a       |')
    print('|                   Log out: l                   |')
    print('--------------------------------------------------')
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
                if (val < len(loc_list) + 1):
                    selected = val - 1
                    return loc_list[selected]
            except ValueError:
                print("Syntax error\n")      
    return None



def offer_ride(driver):
    global connection, cursor    
    
    cursor.execute('SELECT MAX(rno) FROM rides;')
    rides = cursor.fetchall()
    if not rides:
        rno = 1
    else:
        rno = rides[0][0] + 1     
    
    valid = False
    while (valid == False):
        rdate = input('Input date (yyyy-mm-dd): ')
        #https://stackoverflow.com/questions/22061723/regex-date-validation-for-yyyy-mm-dd
        if(re.match('^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$', rdate)):
            valid = True
        else:
            print('Invalid format, please try again.')

    valid = False
    while (valid == False):
        try:
            seats = int(input('Input number of seats offered: '))
            if (seats > 0):
                valid = True
            else:
                print('Invalid number of seats, please try again.')
        except ValueError:
            print('Invalid number of seats, please try again.')

    price = input('Input price per seat: ')
    lugdesc = input('Input luggage description: ')
    
    
    valid = False
    while (valid == False):
        src = input('Input source location: ')
        src_loc = location_list(src)
        if (src_loc is None):
            print("No location found, return to previous.")
        else:
            valid = True
            
            
    valid = False
    while (valid == False):
        dst = input('Input destination location: ')
        dst_loc = location_list(dst)
        if (dst_loc is None):
            print("No location found, return to previous.")
        else:
            valid = True
    
    #Checks if car number is valid if not terminates
    valid = False
    while (valid == False):
        cno = input('Input car number (Blank for null):')
        if (cno == ''):
            valid = True
            data = (rno,price,rdate,seats,lugdesc,src_loc[0],dst_loc[0],driver)
            cursor.execute('INSERT INTO rides(rno, price, rdate, seats, lugDesc, src, dst, driver) VALUES (?,?,?,?,?,?,?,?);',data)
            print('Success!')
        else:
            data = (cno, driver)
            cursor.execute('SELECT cno FROM cars WHERE cno = ? AND owner = ?;', data)
            cnolist = cursor.fetchall()
            if not cnolist:
                print('Invalid cno, please check again.')
            else:
                valid = True
                data = (rno,price,rdate,seats,lugdesc,src_loc[0],dst_loc[0],driver,cno)
                cursor.execute('INSERT INTO rides VALUES (?,?,?,?,?,?,?,?,?);',data)                
    
    while (1):
        print('--------------------------------------------------')
        print('|            [Add enroute locations]             |')
        print('|                                                |')
        print('|               Add one Enroute: e               |')
        print('|           Stop adding and go back: q           |')
        print('--------------------------------------------------')
        s = input('Please select: ')
        if (s.lower() == 'e'):
            enloc = input('Input destination location: ')
            ret_enloc = location_list(enloc)        
            if (ret_enloc is not None):
                #Adds the rno and lcode to the enroute
                lcode = ret_enloc[0]
                values = (rno, lcode)
                cursor.execute('INSERT INTO enroute VALUES (?,?)',values)
                print("Added enroute.\n")
        elif (s.lower() == 'q'):
            connection.commit()
            return 0
        else:
            print("Syntax error\n")
    
    return 0



def ride_menu(email):
    #The member should be able to offer rides by providing a date, the number of seats offered, the price per seat, a luggage description, a source location, and a destination location. The member should have the option of adding a car number and any set of enroute locations. For locations (including source, destination and enroute), the member should be able to provide a keyword, which can be a location code. If the keyword is not a location code, your system should return all locations that have the keyword as a substring in city, province or address fields. If there are more than 5 matching locations, at most 5 matches will be shown at a time, letting the member select a location or see more matches. If a car number is entered, your system must ensure that the car belongs to the member. Your system should automatically assign a unique ride number (rno) to the ride and set the member as the driver of the ride.
    global connection, cursor
    stop = False
    while (stop == False):
        print('--------------------------------------------------')
        print('|                [Offer a ride]                  |')
        print('|                                                |')
        print('|               Offer a ride: o                  |')
        print('|              Stop and go back: s               |')
        print('--------------------------------------------------')        
        value = input('Please select: ')
        if (value.lower() == 's'):
            stop = True
        elif (value.lower() == 'o'):
            offer_ride(email)
        else:
            print("Syntax error\n")
    print('Ride menu stopped\n')
    connection.commit()
    return 0


def bookings_init(email):
    global connection, cursor
    stop = False
    while (stop == False):
        print('--------------------------------------------------')
        print('|         [Book members/cancel bookings]         |')
        print('|                                                |')
        print('|              View/Cancel Bookings: v           |')
        print('|              Book members: b                   |')
        print('|              Stop and go back: s               |')
        print('--------------------------------------------------')        
        value = input('Please select: ')
        if (value.lower() == 's'):
            stop = True
        elif (value.lower() == 'v'):
            booking(email,"v")
        elif (value.lower() == 'b'):
            booking(email,"b")
        else:
            print("Syntax error\n")
    print('Manage Bookings menu stopped\n')
    connection.commit()
    return 0

def booking(email,option):
    global connection, cursor

    if option == "v":
        booking_list = booking_view(email)
        stop = False
        while stop == False:
            if len(booking_list) == 0:
                print("\n")
                return
            key = input('Enter \"s\" to go back OR enter the entry# to cancel booking: ')
            print('\n')
            if (key.lower() == 's'):
                return
            else:
                try:
                    if (int(key) <= len(booking_list) and int(key) >= 0):
                        cursor.execute('DELETE FROM bookings WHERE bno == ?;', (booking_list[int(key)-1][0],))

                        cursor.execute('''SELECT datetime('now', 'localtime');''')
                        time = cursor.fetchall()
                        content = input('Please enter the reason for the cancellation that will be sent to the user: ')
                        data = (booking_list[int(key)-1][1], time[0][0], email, content, booking_list[int(key)-1][6], 'n')
                        cursor.execute('INSERT INTO inbox VALUES (?,?,?,?,?,?);',data)

                        connection.commit()

                        print("\n")
                        booking_list = booking_view(email)

                except ValueError:
                    print("Syntax error\n")

    if option == "b":
        cursor.execute("SELECT rides.rno, rides.seats-bookings.seats, rides.price, rides.src, rides.dst FROM rides, bookings \
            WHERE rides.driver ==:email AND bookings.rno == rides.rno;", {"email":email})

        rides = cursor.fetchall()
        #print(rides)
        if len(rides) == 0:
            print("No listing found.")
            return
        else:
            stop = False
            while stop != True:
                selection = list_scrolling_booking(rides,"ride to add booking")
                if selection == "s":
                    return
                elif (selection != None):
                    stop = True
                    print("Selected entry# %d: " % (selection+1))
                    mEmail = input("Enter email: ")

                    mSeats = input("The number of seats booked: ")
                    mSeats = int(mSeats)

                    mCost = input("the cost per seat: ")
                    mCost = int(mCost)

                    mPickup = input("pickup code: ")
                    mDropoff = input("Drop off code: ")

                    cursor.execute("SELECT bookings.bno FROM bookings;")
                    allbno = cursor.fetchall()
                    bnoList = []
                    for bno in allbno:
                        bnoList.append(bno[0])
                    bnoList.append(1000000)
                    try:
                        mBNO = next(i for i, bno in enumerate(bnoList, 1) if i != bno)
                    except StopIteration:
                        pass

                    data = (mBNO, mEmail, selection+1, mCost, mSeats, mPickup, mDropoff)
                    cursor.execute('INSERT INTO bookings VALUES (?,?,?,?,?,?,?);',data)

                    cursor.execute('''SELECT datetime('now', 'localtime');''')
                    time = cursor.fetchall()
                    content = "You have been booked (%d) by rno (%d)" % (mBNO, (selection+1))
                    data = (mEmail, time[0][0], email, content, selection+1, 'n')
                    cursor.execute('INSERT INTO inbox VALUES (?,?,?,?,?,?);',data)
                    connection.commit()
                    print("Message sent.")
                    return
    
def list_scrolling_booking(thelist, type_name):
    global connection, cursor
    selected = 0
    v = 0
    if (len(thelist) == 0):
        return None
    print("RNO,\tSeats,\tPrice,\tSrc,\tDst")
    while (selected == 0):
        for x in range(v, v+5):
            if (x < len(thelist)): 
                print(str(x+1) + ".) " + str(thelist[x]))                
        print("Input number to select "+type_name+" or input \"s\" to go back to previous menu: ", end="")
        if (v+5 < len(thelist)):
            print("f: Forward")
        if (v != 0):
            print("p: Previous")
        selection = input()
        if (selection.lower() == 'f') and (v+5 < len(thelist)):
            v = v + 5
        elif (selection.lower() == 'p') and (v != 0):
            v = v - 5
        elif (selection.lower() == 's'):
            return "s"
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

def booking_view(email):
    global connection, cursor

    cursor.execute("SELECT bookings.bno, bookings.email, bookings.seats, ifnull(bookings.cost,rides.price), ifnull(bookings.pickup,rides.src), ifnull(bookings.dropoff,rides.dst), rides.rno FROM rides, bookings WHERE rides.driver ==:email AND bookings.rno == rides.rno;", {"email":email})
    booking_list = cursor.fetchall()

    if len(booking_list) != 0:
        for i, booking in enumerate(booking_list, 1):
            print(str(i) + ".) " + "(" + str(booking[0]), end=" , ")
            print(booking[1], end=" , ")
            print(booking[2], end=" , ")
            print(booking[3], end=" , ")
            print(booking[4], end=" , ")
            print(booking[5]+")")

        print('\n')
    else:
        print("No listing found.")

    return (booking_list)


def main():
    connect('./test.db')
    email = LoginOrRegister()
    while(1):
        DisplayMenu()
        key = input('Please select: ')
        print('\n')
        if (key.lower() == 'o'):
            ride_menu(email)
        elif(key.lower() == 's'):
            print('Search for ridese not finished yet')
        elif(key.lower() == 'b'):
            bookings_init(email)
        elif(key.lower() == 'p'): 
            PostRideRequests(email)
        elif(key.lower() == 'a'): 
            SearchaDeleteRideRequests(email)
        elif(key.lower() == 'l'):
            connection.commit()
            connection.close()            
            main()
        else:
            print('Invalid selection, please try again.')

    return 0
    
    
    
main()
