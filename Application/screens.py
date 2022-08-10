# Used to clear the terminal screen
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
def clear(timer=LOW_TIMER):

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
                   '\n[ 2 ] My borrowed books'
                   '\n[ 3 ] Logout\n')
            
            menu = ['1', '2', '3']

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
        
        # User borrowed books
        elif option == '2': 
            user_borrowed_books(cnx)

        # Logout to user screen
        elif option == '3': 
            cnx.close()
            screen_transition_message('Closing connection...')
            return

# Interface for librarians
def librarian_menu(cnx):

    # Extracts the user name
    user = cnx.user

    while True:
        clear()
        while True:
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                  f'Welcome, {user}\n!'
                  '\n[ 1 ] Consult books'
                  '\n[ 2 ] Consult users'
                  '\n[ 3 ] Borrow requests'
                  '\n[ 4 ] Consult borrowed books'
                  '\n[ 5 ] Logout\n')

            # Gets the option typed
            option = input("Enter the desired operation: ")
            menu = ['1', '2', '3', '4']

            # Checks if the option exists
            if option not in menu:
                screen_transition_message()
            
            # Otherwise, skips to the next block
            else:
                break
    
        # Consult books
        if option == '1': 
            consult_books(cnx)

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

# Interface for administrators
def admin_menu(cnx):

    # Extracts the user name
    user = cnx.user

    while True:
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
              f'Welcome, {user}!\n'
              '\n[ 1 ] Register user'
              '\n[ 2 ] Remove user'
              '\n[ 3 ] Register book'
              '\n[ 4 ] Consult books'
              '\n[ 5 ] Borrow requests'
              '\n[ 6 ] Logout\n')

        # Gets the option typed
        option = input("Enter the desired operation: ")
        menu = ['1', '2', '3', '4', '5', '6']

        # Checks if the option exists
        if option not in menu:
            screen_transition_message()

        # Otherwise, skips to the next block
        else:
            break

    # Register user
    if option == '1': 
        register_user(cnx)

    # Remove user
    elif option == '2': 
        remove_user(cnx)
    
    # Register book
    elif option == '3': 
        register_book(cnx)

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


# Screen for book consultation
def consult_books(cnx, user_acess='user'):

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

    # This block is only displayed for common users
    if user_acess == 'user':
        while True:
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                f'Displaying results for "{title}": '
                f'{ANSI_YELLOW}{books}{ANSI_RESET}'
                '\nDo you want to reserve one of the titles?'
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

    # If not a regular user, this block is executed
    else:
        entry = input('To return, press anything.')

        if entry != '':
            return

# Displays specific users
def consult_users(cnx):
    while True:
        clear()

        # Loop to receive the username
        while True:
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

            # Gets the option typed
            name = input("Enter username: ")

            # Checks if the entered name is valid
            if name.isspace() or len(name) < 3:
                screen_transition_message('Empty field or too short. Please try again')
            
            # Gets a dataframe with the search result
            users = db.get_users(name, cnx)

            # If there are no results, an error message is displayed
            if users.empty:
                screen_transition_message(f'No results for "{name}". Please try again.', timer = BIG_TIMER)
                continue

            # Otherwise, skips to the next block
            else:
                break

        # Loop that displays found users
        while True:
            clear()
            print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
                  f'Results for "{name}": '
                  f'{ANSI_YELLOW}{name}{ANSI_RESET}\n')

            entry = input('To return, press anything.')

            if entry != '':
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

                # Extracts the title of the chosen book
                title = books["title"][0]

                # Calls the internal method responsible for confirming the reservation
                # and terminate the thread if no errors occur
                db.reserve_book(title, isbn_code, cnx)

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
            index = int(input('\nEnter the index of the book you want to book: '))

            # Checks if the index exists
            if index not in range(book_count):
                screen_transition_message(f'There is no book with index {index}. Please try again.')

            # If the index is correct, this block is executed
            else:

                # Extracts the ISBN code of the chosen book
                isbn_code = books["isbn_code"][index]

                # Extracts the title of the chosen book
                title = books["title"][index]

                # Calls the internal method responsible for confirming the reservation
                # and terminate the thread if no errors occur
                db.reserve_book(title, isbn_code, cnx)

                # Displays a message notifying the user that the operation is complete
                screen_transition_message('Done! your book is waiting. Ask a librarian to authorize the loan.')
                return True
    
# Displays all user borrowed_books
def user_borrowed_books(cnx):
    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
              f'My borrowed_books:\n')

        # Gets a dataframe containing all user borrowed_books
        borrowed_books = db.my_loans(cnx)

        # If there are no borrowed_books, a warning screen is displayed, ending the thread
        if borrowed_books.empty:
            screen_transition_message('You dont have any borrowed books yet.\nReturning to main menu.', timer=BIG_TIMER)
            return
    
# Screen that displays all the reservations of a user
def borrow_requests(cnx):
    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}')

        # Receives the user's registration for later consultation
        registration = input(f'Enter user registration:\n')

        # Gets a dataframe with all reservations from the specified user
        reservations = db.get_reservations(registration, cnx)

        # If there are no borrowed_books, a warning screen is displayed
        if reservations.empty:
            screen_transition_message(f'There are no reservations for the user with registration "{registration}".', timer=BIG_TIMER)

        # Otherwise, skips to the next block
        else:
            break
    
     # Extracts the number of user reservations
    reservation_count = reservations[reservations.columns[0]].count()

    while True:
        clear()
        print(f'{ANSI_CYAN}=-=-=-=-- Azure Library --=-=-=-=\n{ANSI_RESET}'
              f'Displaying all reservations made for the registration user "{matricula}":\n'
              f'{ANSI_YELLOW}{reservations}{ANSI_RESET}')

        # Receives the value of the index, being exclusively integers
        index = int(input('\nEnter the index of the request to confirm it: '))

        # Checks if the index exists
        if index not in range(reservation_count):
            screen_transition_message(f'There is no reservation with index {index}. Please try again.')

        # If the index is correct, this block is executed
        else:

            # Extracts the ISBN code of the chosen book
            isbn_code = reservations["isbn_code"][index]

            # Extracts the title of the chosen book
            title = reservations["title"][index]

            # Calls the internal method responsible for confirming the reservation
            # and terminate the thread if no errors occur
            db.borrow_book(title, registration, isbn_code, cnx)

            # Displays a message notifying the user that the operation is complete
            screen_transition_message('Done! borrowing confirmed.')
            return True
            