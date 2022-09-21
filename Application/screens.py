# Used to change_screen the terminal screen
from os import system

# Allows you to hide the typed password
from getpass import getpass

# Allows smoother transitions between interfaces
from time import sleep

# Ensure correct connection and dialog between application and database
import db_connection as db

# ANSI codes to change output color
ANSI_CYAN = '\033[1;36m'
ANSI_RED = '\033[1;31m'
ANSI_YELLOW = '\033[1;33m'
ANSI_RESET = '\033[0m'

# Setting default timers for screen transitions
LOW_TIMER = 0.5
MED_TIMER = 2
BIG_TIMER = 6

# Clear the terminal screen
def change_screen(timer=BIG_TIMER):

    # Simple counter to smooth transitions
    sleep(timer)
    _ = system('clear')

    # Prints a head with the app's name
    print(f"""{ANSI_CYAN}----- Azure Library -----{ANSI_RESET}\n""")

# A message that is displayed when the screen is reloaded or changed
def screen_transition_message(message="", timer=MED_TIMER):
    
    print(ANSI_RED + message + ANSI_RESET)
    change_screen(timer)

# User screen that guarantees the correct initialization of the cnx
def login():
    change_screen()
    while True:                  

        # Gets publisher's name
        while True:
            user = input("Enter your login: ")

            # Checks if user is empty
            if user.isspace():
                screen_transition_message('Login is empty. Please retype.')
                continue

            # Checks user lenght
            if len(user) < 3:
                screen_transition_message('Too short (<3). Please retype.')
                continue
            
            break

        # Gets password
        while True:
            password = getpass("Enter your password: ")

            # Checks if password is empty
            if password.isspace():
                screen_transition_message('Login is empty. Please retype.')
                continue

            # Checks password lenght
            if len(password) < 3:
                screen_transition_message('Too short (<3). Please retype.')
                continue
            
            break       

        # Connector that will be used throughout the application
        cnx = db.access_database(user, password)

        # Checks for connection error
        if cnx == "ER_ACCESS_DENIED_ERROR":
            screen_transition_message('Incorrect user name or password. Try again.')
            return 'error'

        elif cnx == "ER_BAD_DB_ERROR":
            screen_transition_message('The system is not accessible at the moment. Try again later.')
            return 'error'

        # If the connection is established, skips to the next block
        else:
            break

    # Checks the access level of the logged in user,
    # being 'admin', 'librarian' or 'user'
    user_acess = db.get_user_acess(user, cnx)

    return user_acess, cnx

# Invoke the main menu for common users
def user_menu(cnx):

    # Extracts the user name
    user = cnx.user

    while True:
        change_screen()

        while True:                
            print(f'Welcome, {user}!\n'
                   '\n[ 1 ] Consult books'
                   '\n[ 2 ] My reserved books'
                   '\n[ 3 ] My borrowed books'
                   '\n[ 4 ] Logout\n')
            
            menu = ['1', '2', '3', '4']

            # Gets the option typed
            option = input("Enter the desired operation: ")

            # Checks if the option exists
            if option not in menu:
                screen_transition_message()
                continue
            
            # Otherwise, skips to the next block
            break

        # Consult books
        if option == '1': 
            consult_books(cnx)

        # User reserved books
        elif option == '2': 
            user_reserved_books(cnx)
        
        # User borrowed books
        elif option == '3': 
            user_borrowed_books(cnx)

        # Logout to user screen
        elif option == '4': 
            cnx.close()
            screen_transition_message('Closing connection...')
            return


# Screen for book consultation
def consult_books(cnx, common_user=True):

    # Control variable to ensure the title is correct
    empty_result = True

    while empty_result:
        while empty_result:
            change_screen()            

            # Gets the book title
            title = input('Enter the title of the book: ')

            # Checks if the title entered is valid
            if title.isspace() or len(title) < 3:
                screen_transition_message('Empty text or too short. Please retype')
                continue

            # If the title is correct, skips to the next block
            break                

        # Displays the filter menu to filter the search result
        while True:
            change_screen()            

            # Gets the filter option
            print('Search books by: '
                  '\n[ 1 ] None'
                  '\n[ 2 ] Category'
                  '\n[ 3 ] Publisher'
                  '\n[ 4 ] Release'
                  '\n[ 5 ] Author\n')

            menu = ['1', '2', '3', '4', '5']
            filter = input('Enter the desired filter: ')

            # Checks if the filter exists
            if filter not in menu:
                screen_transition_message()
                continue

            # Gets a dataframe with the search result
            books = db.get_books(title, filter, cnx)

            # If there are no results, an error message is displayed
            if books.empty:
                screen_transition_message('No results. Try again.', timer = BIG_TIMER)
                break

            # If the filter is correct, skips to the next block            
            empty_result = False
            break

    
    while True:
        change_screen()
        
        print(f'Displaying results for "{title}":\n'
              f'{ANSI_YELLOW}{books}{ANSI_RESET}')

        # This block is only displayed for common users
        if common_user:
            print('\nDo you want to reserve one of the titles?'
                    '\n[ 1 ] Yes'
                    '\n[ 2 ] No\n')

            # Gets the option typed
            option = input("Enter the desired operation: ")
            menu = ['1', '2']

            # Checks if the option exists
            if option not in menu:
                screen_transition_message()
                continue

            # If the user decides to book, the 'book_reservations' screen is called
            # Then the thread is terminated
            elif option == '1':
                book_reservations(books, cnx)
                return

            # Otherwise, this thread is terminated
            elif option == '2':
                screen_transition_message('Returning to main menu.')
                return

        _ = input('\nTo return, press anything.')
        return            


# Screen responsible for book reservations
def book_reservations(books, cnx):
    
    # Extracts the number of books resulting from the search
    book_count = books[books.columns[0]].count()

    # If there is only one book resulting from the search, this block is started
    if (book_count) == 1:
        while True:
            change_screen()
            
            print(f'Do you want to reserve the book: "{books["title"][0]}"?'
                   '\n[ 1 ] Yes'
                   '\n[ 2 ] No\n')

            menu = ['1', '2']

            # Gets the option typed by the user
            option = input('Enter an option: ')

            # Checks if the option exists
            if option not in menu:
                screen_transition_message()
                continue

            # If the user chooses to reserve, this block is executed
            elif option == '1':

                # Extracts the ISBN code of the chosen book
                isbn_code = books["isbn_code"][0]                

                # Calls the internal method responsible for confirming the reservation
                # and terminate the thread if no errors occur
                db.reserve_book(isbn_code, cnx)

                return

            # If the user does not want to reserve any books, the thread is closed
            elif option == '2':
                screen_transition_message('Returning to main menu...')
                return
    
    # If there is more than one result, this block is executed    
    while True:
        change_screen()
        
        # Prints search results
        print(f'{ANSI_YELLOW}{books}{ANSI_RESET}')

        # Receives the value of the index, being exclusively integers
        index = int(input('\nEnter the index of the book you want to reserve: '))

        # Checks if the index exists
        if index not in range(book_count):
            screen_transition_message(f'There is no book with index {index}. Please try again.', timer=BIG_TIMER)
            continue        

        # Extracts the ISBN code of the chosen book
        isbn_code = books["isbn_code"][index]                

        # Calls the internal method responsible for confirming the reservation
        # and terminate the thread if no errors occur
        db.reserve_book(isbn_code, cnx)

        # Displays a message notifying the user that the operation is complete
        print('Done! your book is waiting.\n')
        
        _ = input('To return, press anything.')
        return True


# Shows all users reserved books
def user_reserved_books(cnx):

    # Gets a dataframe containing all reservations
    reservations = db.user_reserved_books(cnx)

    while True:
        change_screen()
        
        print('My reservations:\n'
             f'{reservations}\n')

        _ = input('To return, press anything.')
        return            


# Displays all user borrowed_books
def user_borrowed_books(cnx):

    # Gets a dataframe containing all user borrowed_books
    user_borrowed_books = db.get_user_borrowed_books(cnx)    

    while True:
        change_screen()
        
        print('My borrowed books:\n'
             f'{user_borrowed_books}\n')

        _ = input('To return, press anything.')
        return


# Interface for librarians
def librarian_menu(cnx):

    # Extracts the user name
    user = cnx.user

    while True:
        change_screen()

        while True:            
            print(f'Welcome, {user}!\n'
                    '\n[ 1 ] Consult books'
                    '\n[ 2 ] Consult users'
                    '\n[ 3 ] Borrow requests'
                    '\n[ 4 ] Consult borrowed books'
                    '\n[ 5 ] Logout\n')

            # Gets the option typed
            option = input("Enter the desired operation: ")
            menu = ['1', '2', '3', '4', '5']

            # Checks if the option exists
            if option not in menu:
                screen_transition_message()
                continue
            
            # Otherwise, skips to the next block            
            break
    
        # Consult books
        if option == '1': 
            consult_books(cnx, common_user=False)

        # Consult users
        elif option == '2': 
            consult_users(cnx)

        # Borrow requests
        elif option == '3':
            borrow_requests(cnx)

        # Consult borrowed books
        elif option == '4':
            consult_borrowed_books(cnx)

        # Logout
        if option == '5': 
            cnx.close()
            screen_transition_message('Closing connection...')
            return


# Displays specific users
def consult_users(cnx):
    while True:
        change_screen()

        # Loop to receive the username
        while True:                        

            # Gets the user name to be found
            login = input("Enter user login: ")

            # Checks if the entered name is valid
            if login.isspace() or len(login) < 3:
                screen_transition_message('Empty field or too short. Please try again')
            
            # Gets a dataframe with the search result
            user = db.get_user(login, cnx)

            # If there are no results, an error message is displayed
            if user.empty:
                screen_transition_message(f'No results for "{login}". Please try again.', timer = BIG_TIMER)
                continue

            # Otherwise, skips to the next blocks
            else:
                break

        # Loop that displays found users
        while True:
            change_screen()
                              
            print(f'{ANSI_YELLOW}{user}{ANSI_RESET}\n')
                        
            _ = input('To return, press anything.')
            return
            

# Screen that displays all the reservations of a user
def borrow_requests(cnx):
    while True:
        change_screen()    

        # Receives the user's registration for later consultation
        registration = input(f'Enter user registration: ')

        # Gets a dataframe with all reservations from the specified user
        reservations = db.get_reservations(registration, cnx)

        # If there are no borrowed_books, a warning screen is displayed
        if reservations.empty:
            print(f'There are no reservations for the user with registration "{registration}".')
            return

        # Otherwise, skips to the next block
        break
    
     # Extracts the number of user reservations
    reservation_count = reservations[reservations.columns[0]].count()

    while True:
        change_screen()
        
        print(f'Displaying all reservations made for the registration "{registration}":\n\n'
              f'{ANSI_YELLOW}{reservations}{ANSI_RESET}\n')

        # Receives the value of the index, being exclusively integers
        index = int(input('Enter the index of the request to confirm it: '))

        # Checks if the index exists
        if index not in range(reservation_count):
            print(f'There is no reservation with index {index}.')

        # If the index is correct, this block is executed
        else:

            # Extracts the ISBN code of the chosen book
            isbn_code = reservations["isbn_code"][index]            

            # Calls the internal method responsible for confirming the reservation
            # and terminate the thread if no errors occur
            db.borrow_book(registration, isbn_code, cnx)

            # Displays a message notifying the user that the operation is complete
            print('Done! borrowing confirmed.')

            _ = input('To return, press anything.')
            return


# Displays all borrowed books
def consult_borrowed_books(cnx):

    # Gets a dataframe containing all borrowings
    borrowed_books = db.get_borrowed_books

    while True:
        change_screen()
        
        print(f'{borrowed_books}\n')

        _ = input('To return, press anything.')
        return


# Interface for administrators
def admin_menu(cnx):

    # Gets logged user name
    user = cnx.user

    while True:
        change_screen()
        
        print(f'Welcome, {user}!\n'
              '\n[ 1 ] Register an user'
              '\n[ 2 ] Remove an user'
              '\n[ 3 ] Register a book'
              '\n[ 4 ] Remove a book'
              '\n[ 5 ] Consult books'
              '\n[ 6 ] Borrow requests'
              '\n[ 7 ] Logout\n')

        # Gets the option typed
        option = input("Enter the desired operation: ")
        menu = ['1', '2', '3', '4', '5', '6']

        # Checks if the option exists
        if option not in menu:
            screen_transition_message()
            continue

        # Otherwise, skips to the next block
        break            

    # Register an user
    if option == '1': 
        register_user(cnx)

    # Remove an user
    elif option == '2': 
        remove_user(cnx)
    
    # Register a book
    elif option == '3': 
        register_book(cnx)

    # Remove a book
    elif option == '4': 
        remove_book(cnx)

    # Consult books
    elif option == '5': 
        consult_books(cnx)

    # Borrow requests
    elif option == '6': 
        borrow_requests(cnx)

    # Logout
    elif option == '7': 
        cnx.close()
        screen_transition_message('Closing connection...')
        return


# Registers a new user on the database
def register_user(cnx):
    while True:
        change_screen()        

        login = input("Enter new user's login: ")

        # Checks if the login already exists
        if not db.get_user(login, cnx).empty:
            print('\nThe inserted login is already in use. Try again.')    

        break

    while True:
        change_screen()        

        password = input("Enter new user's password (length >= 4): ")

        if len(password) < 4:
            print('This password is too short.')
            continue

        if not password.isspace:
            print('Please enter a non space filled password.')
            continue

        break

    # Defines new user's acess level
    while True:
        change_screen()        

        print('Enter the acess level:\n' 
              '[ 1 ] Common user\n'
              '[ 2 ] Librarian\n'
              '[ 3 ] Administrator\n')

        acess = input('\nEnter the desired option: ')
        menu =  ['1', '2', '3']

        if acess not in menu:
            print('Please enter a valid option.')
            continue

        break

    # Receives all aditional data for common user registration
    if acess == '1':

        # Collects general and specific data depending on new user's category 
        while True:
            change_screen()            

            print("Enter new user's category:\n"
                  '[ 1 ] Student\n'
                  '[ 2 ] Employee\n'
                  '[ 3 ] Professor\n')
            
            user_type = input('\nEnter the desired option: ')

            menu =  ['1', '2', '3']

            if user_type not in menu:
                print('Please enter a valid option.')
                continue

            break
        
        # Receives new user's real name
        while True:
            change_screen()            
                        
            name = input("Enter new user's full name: ")

            if len(name) < 4:
                print('Not enough characters for a name (MIN=5).')
                continue

            break

        # Receives new user's adress
        while True:
            change_screen()            
                        
            adress = input("Enter new user's adress: ")

            if len(adress) < 4:
                print('Not enough characters for an adress (MIN=5).')
                continue

            break
                                

        # Data for 'Student'
        if user_type == '1':            
            change_screen()                                  

            # Receives student's entry date
            while True:
                change_screen()            
                _entry_date = input("Enter hiring date (Ex: 2024-02-06): ")

                # Splits date components to validate it
                date = _entry_date.split('-')                                

                # Checks if date components are valid
                try:
                    entry_date = date(date[0], date[1], date[2]).strftime('%Y-%m-%d')                    
                    break

                except ValueError:                    
                    print(f'Invalid date values: "{_entry_date}"')
                    continue              

            # Receives student's expected completition date
            while True:
                change_screen()            

                _expected_completition_date = input("Enter expected completition date (Ex: 2024-02-06): ")

                # Splits date components to validate it
                date = _expected_completition_date.split('-')                                

                # Checks if date components are valid
                try:
                    expected_completition_date = date(date[0], date[1], date[2]).strftime('%Y-%m-%d')                    
                    break                

                except ValueError:                    
                    print(f'Invalid date values: "{_expected_completition_date}"')
                    continue


            # Receives student's course code
            while True:
                change_screen()  
                course_code = input("Enter the course code: ")

                # Checks if course code is correct
                course_count = db.get_course_count(cnx)

                if not course_code.isnumeric or int(course_code) not in range(1, course_count+1):
                    print(f'Please enter a numeric between 1 and {course_count}.')
                    continue

                break

            user_data = {'user_type':'student', 'name':name, 'entry_date':entry_date,
                        'expected_completition_date':expected_completition_date, 
                        'adress':adress, 'course_code':course_code}

        # Data for 'Employee'
        if user_type == '2':            
            user_data = {'user_type':'employee', 'name':name,'adress':adress}

        # Data for 'Professor'
        if user_type == '3':            
            while True:
                change_screen()                            

                _hiring_date = input("Enter hiring date (Ex: 2024-02-06): ")

                # Splits date components to validate it
                date = _hiring_date.split('-')                                

                # Checks if date components are valid
                try:
                    hiring_date = date(date[0], date[1], date[2]).strftime('%Y-%m-%d')  
                    break                                      

                except ValueError:                    
                    print(f'Invalid date values: "{_hiring_date}"')
                    continue

            # Receives work regime correctly
            while True:
                change_screen()     

                work_regime = input("Enter the work regime (DE, 40h, 20h): ")

                # Checks if input is valid
                if work_regime not in ['DE', '40h', '20h']:
                    print('Invalid entry for work regime.')
                    continue

                break

            # Receives cell phone 
            while True:
                change_screen()       

                # Receives professor's cell phone
                cell_phone = input('Enter the cell phone: ')

                # Checks if given cell phone is numerical            
                if not cell_phone.isnumeric:
                    print(f'Please enter a numeric between 1 and {course_count}.')
                    continue

                break

            # Receives course code
            while True:
                change_screen()   

                # Checks if course code is correct
                course_count = db.get_course_count(cnx)

                if not course_code.isnumeric or int(course_code) not in range(1, course_count+1):
                    print(f'Please enter a numeric between 1 and {course_count}.')
                    continue

                break

            user_data = {'user_type':'professor', 'name':name, 'hiring_date':hiring_date, \
                        'work_regime':work_regime, 'adress':adress, 'cell_phone':cell_phone, 'course_code':course_code}

        # Runs a script to create the new user on the database
        db.register_user(login, password, cnx, user_data)        

    elif acess == '2':
        db.register_user(login, password, cnx, acess='librarian')

    elif acess == '3':
        db.register_user(login, password, cnx, acess='admin')

    print(f'User {login} created sucessfully! Returning to main menu...')
    return


# Removes a user from database based on its login
def remove_user(cnx):
    while True:
        change_screen()

        login = input("Enter user's login")

        # Confirmation dialog before deleting a user
        while True:
            change_screen()

            option = input(f'Are you sure you want to remove {login}?\n'
                            '[ 1 ] Yes\n'
                            '[ 2 ] No\n'
                            '\nInput: ')
            
            menu = ['1', '2']

            if option not in menu:
                screen_transition_message()
                continue
                
            break
        
        # Calls a method that deletes a given user
        db.delete_user(login, cnx)


# Registers a new book in the database
def register_book(cnx):
    while True:
        change_screen()

        print("Please enter the following information about the new book:\n")

        # Gets book's isbn code
        while True:
            isbn_code = input("ISBN code: ")

            # Checks if isbn code is numeric
            if not isbn_code.isnumeric():
                screen_transition_message('Only numeric allowed. Please retype.')
                continue

            # Checks isbn lenght
            if len(isbn_code) < 10:
                screen_transition_message('Too short (<10). Please retype.')
                continue

            break    

        # Gets book's title
        while True:
            title = input("Title: ")

            # Checks if title is empty
            if title.isspace():
                screen_transition_message('Title is empty. Please retype.')
                continue

            # Checks title lenght
            if len(title) < 3:
                screen_transition_message('Too short (<3). Please retype.')
                continue
            
            break
        
        # Gets book's release year
        while True:
            release_year = input("Release year (YYYY): ")

            # Checks if release_year is numeric
            if not release_year.isnumeric():
                screen_transition_message('Only numeric allowed. Please retype.')
                continue

            # Checks release_year length
            if len(release_year) != 4:
                screen_transition_message('Invalid input length (!= 4). Please retype.')
                continue
            
            break
        
        # Gets publisher's name
        while True:
            publisher = input("Publisher: ")

            # Checks if publisher is empty
            if publisher.isspace():
                screen_transition_message('Publisher is empty. Please retype.')
                continue

            # Checks publisher lenght
            if len(publisher) < 3:
                screen_transition_message('Too short (<3). Please retype.')
                continue
            
            break

        # Gets category code            
        while True:
            category_code = input("Category code: ")

            # Checks if category_code is numeric
            if not category_code.isnumeric():
                screen_transition_message('Only numeric allowed. Please retype.')
                continue

            # Checks category_code is in a valid range
            count = db.get_category_count(cnx)

            if category_code not in range(1, count):
                screen_transition_message('Specified category does not exist. Please retype.')
                continue
            
            break
                
        # Gets total of copies available
        while True:
            copies_available = input("Copies: ")

            # Checks if copies_available is numeric
            if not copies_available.isnumeric():
                screen_transition_message('Only numeric allowed. Please retype.')
                continue            
            
            break    
        
        data = {'isbn_code':isbn_code, 'title':title, 'release_year':release_year, \
                     'publisher':publisher, 'category_code':category_code, 'copies_available':copies_available}


        # Registers the book in the database
        db.register_book(data, cnx)
    

# Removes a book from the database
def remove_book(cnx):
    while True:
        change_screen()   
        
        # Gets book's isbn code
        while True:
            isbn_code =  input("Enter book's ISBN code: ")

            # Checks if isbn code is numeric
            if not isbn_code.isnumeric():
                screen_transition_message('Only numeric allowed. Please retype.')
                continue

            # Checks isbn lenght
            if len(isbn_code) < 10:
                screen_transition_message('Too short (<10). Please retype.')
                continue

            break    

        # Calls a method to remove the book from the database
        db.remove_book(isbn_code, cnx)

