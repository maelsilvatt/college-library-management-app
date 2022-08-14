# Used to clear the terminal screen
from curses.ascii import isspace
from os import system

# Allows you to hide the typed password
from getpass import getpass

# Allows smoother transitions between interfaces
from time import sleep

# Ensure correct connection and dialog between application and database
import mysql_connection as db

# ANSI codes to change output color
ANSI_CYAN = '\033[1;36m'
ANSI_RED = '\033[1;31m'
ANSI_YELLOW = '\033[1;33m'
ANSI_RESET = '\033[0m'

# Setting default timers for screen transitions
LOW_TIMER = 0.5
MED_TIMER = 1
BIG_TIMER = 4

# Clear the terminal screen
def clear(timer=BIG_TIMER):

    # Simple counter to smooth transitions
    sleep(timer)
    _ = system('clear')

# A message that is displayed when the screen is reloaded or changed
def screen_transition_message(message="Invalid entry. Try again.", timer=MED_TIMER):
    
    print(ANSI_RED + message + ANSI_RESET)
    clear(timer)

# User screen that guarantees the correct initialization of the cnx
def login():
    clear()
    while True:
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')
        user = input("Enter your user name: ")
        password = getpass("Enter your password: ")

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
        clear()
        while True:
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                  f'Welcome, {user}!\n'
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
            
            # Otherwise, skips to the next block
            else:
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
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

            # Gets the book title
            title = input('Enter the title of the book: ')

            # Checks if the title entered is valid
            if title.isspace() or len(title) < 3:
                screen_transition_message('Empty text or too short. Please retype')

            # If the title is correct, skips to the next block
            else:
                break

        # Displays the filter menu to filter the search result
        while True:
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

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
            else:
                empty_result = False
                break

    
    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
            f'Displaying results for "{title}":\n'
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

            # If the user decides to book, the 'book_reservations' screen is called
            # Then the thread is terminated
            elif option == '1':
                if book_reservations(books, cnx):
                    return

            # Otherwise, this thread is terminated
            elif option == '2':
                screen_transition_message('Returning to main menu.')
                return

        else:
            _ = input('\nTo return, press anything.')
            return            


# Screen responsible for book reservations
def book_reservations(books, cnx):
    
    # Extracts the number of books resulting from the search
    book_count = books[books.columns[0]].count()

    # If there is only one book resulting from the search, this block is started
    if (book_count) == 1:
        while True:
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                  f'Do you want to reserve the book: "{books["title"][0]}"?'
                  '\n[ 1 ] Yes'
                  '\n[ 2 ] No\n')

            menu = ['1', '2']

            # Gets the option typed by the user
            option = input('Enter an option: ')

            # Checks if the option exists
            if option not in menu:
                screen_transition_message()

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
    else:
        while True:
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                  f'{ANSI_YELLOW}{books}{ANSI_RESET}')

            # Receives the value of the index, being exclusively integers
            index = int(input('\nEnter the index of the book you want to reserve: '))

            # Checks if the index exists
            if index not in range(book_count):
                screen_transition_message(f'There is no book with index {index}. Please try again.', timer=BIG_TIMER)

            # If the index is correct, this block is executed
            else:

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
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                'My reservations:\n'
                f'{reservations}\n')            

        _ = input('To return, press anything.')
        return            


# Displays all user borrowed_books
def user_borrowed_books(cnx):

    # Gets a dataframe containing all user borrowed_books
    user_borrowed_books = db.get_user_borrowed_books(cnx)    

    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
              'My borrowed books:\n'
              f'{user_borrowed_books}\n')

        _ = input('To return, press anything.')
        return


# Interface for librarians
def librarian_menu(cnx):

    # Extracts the user name
    user = cnx.user

    while True:
        clear()
        while True:
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                  f'Welcome, {user}!\n'
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
            
            # Otherwise, skips to the next block
            else:
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
        clear()

        # Loop to receive the username
        while True:            
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

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
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'                  
                  f'{ANSI_YELLOW}{user}{ANSI_RESET}\n')
                        
            _ = input('To return, press anything.')
            return
            

# Screen that displays all the reservations of a user
def borrow_requests(cnx):
    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

        # Receives the user's registration for later consultation
        registration = input(f'Enter user registration: ')

        # Gets a dataframe with all reservations from the specified user
        reservations = db.get_reservations(registration, cnx)

        # If there are no borrowed_books, a warning screen is displayed
        if reservations.empty:
            print(f'There are no reservations for the user with registration "{registration}".')
            return

        # Otherwise, skips to the next block
        else:
            break
    
     # Extracts the number of user reservations
    reservation_count = reservations[reservations.columns[0]].count()

    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
              f'Displaying all reservations made for the registration "{registration}":\n\n'
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

            return True


# Displays all borrowed books
def consult_borrowed_books(cnx):

    # Gets a dataframe containing all borrowings
    borrowed_books = db.get_borrowed_books

    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-={ANSI_RESET}\n\n'
              f'{borrowed_books}\n')

        _ = input('To return, press anything.')
        return


# Interface for administrators
def admin_menu(cnx):

    # Extracts the user name
    user = cnx.user

    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
              f'Welcome, {user}!\n'
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

        # Otherwise, skips to the next block
        else:
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
    elif option == '3': 
        remove_book(cnx)

    # Consult books
    elif option == '4': 
        consult_books(cnx)

    # Borrow requests
    elif option == '5': 
        borrow_requests(cnx)

    # Logout
    elif option == '6': 
        cnx.close()
        screen_transition_message('Closing connection...')
        return

# Registers a new user on the system
def register_user(cnx):
    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

        login = input("Enter new user's login: ")

        if db.get_user(login, cnx).empty:
            break

        print('\nThe inserted login is already in use. Try again.')

    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

        password = input("Enter new user's password (length >= 4): ")

        if len(password) < 4:
            print('This password is too short.')
            continue

        if password.isspace:
            print('Please enter a non space filled password.')
            continue

        break
    
    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

        acess = input('Enter the acess level:\n' 
                      '[ 1 ] Common user\n'
                      '[ 2 ] Librarian\n'
                      '[ 3 ] Administrator\n')
        
        menu =  ['1', '2', '3']

        if acess not in menu:
            print('Please enter a valid option.')
            continue

        break

    if acess == '1':
        while True:
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

            user_type = input("Enter user's category:\n"
                        '[ 1 ] Student\n'
                        '[ 2 ] Employee\n'
                        '[ 3 ] Professor\n')
            
            menu =  ['1', '2', '3']

            if user_type not in menu:
                print('Please enter a valid option.')
                continue

            registration = input("Enter the registration: ")

            name = input("Enter the name: ")

            adress = input("Enter the adress: ")
            
            break

        if user_type == '1':            
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')                

            entry_date = input("Enter the entry date (YYYY-mm-dd): ")

            expected_completition_date = input("Enter the expected completition date (YYYY-mm-dd): ")

            course_code = input("Enter the course code: ")

            user_data = {'user_type':'student', 'registration':registration, 'name':name, 'entry_date':entry_date, \
                        'expected_completition_date':expected_completition_date, 'adress':adress, 'course_code':course_code}

        if user_type == '2':
            user_data = {'user_type':'employee', 'registration':registration, 'name':name,'adress':adress}

        if user_type == '3':            
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')                

            hiring_date = input("Enter the entry date (YYYY-mm-dd): ")

            work_regime = input("Enter the work regime (DE, 40h, 20h): ")

            cell_phone = input("Enter the cell phone: ")

            course_code = input("Enter the course code: ")

            user_data = {'user_type':'professor', 'registration':registration, 'name':name, 'hiring_date':hiring_date, \
                        'work_regime':work_regime, 'adress':adress, 'cell_phone':cell_phone, 'course_code':course_code}

        db.register_user(login, password, cnx, user_data)        

    elif acess == '2':
        register_user(login, password, cnx, acess='librarian')

    elif acess == '3':
        register_user(login, password, cnx, acess='admin')

    print(f'User {login} created sucessfully!')
    return



