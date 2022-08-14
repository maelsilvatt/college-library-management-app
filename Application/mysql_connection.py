# Enables the communication between the main app and the database
import mysql.connector

# Makes it easier to manipulate query results converting them to dataframes
from pandas import DataFrame

# Enables date manipulation to calculate insertions that require DATE format
from datetime import datetime

# Initialize the connector responsible for the immediacy between the application
# and the database
def access_database(user, password):
    try:
        # These are the input data for the database connection
        acess_data = {
            'host': 'localhost',
            'database': 'college_library_db',
            'user': user,
            'password': password
        }

        # Instantiates a connector, allowing dialog between the software and the database
        cnx = mysql.connector.connect(**acess_data)

        return cnx
        
    except mysql.connector.Error as error:

        # In case of incorrect login data, this block is executed
        if error.errno == 'ER_ACCESS_DENIED_ERROR':
            return 'ER_ACCESS_DENIED_ERROR'

        # If the database malfunctions, this block is executed
        elif error.errno == 'ER_BAD_DB_ERROR':
            return 'ER_BAD_DB_ERROR'

        # If there is another type of error, this block is executed
        else:
            return error


# Executes a query, returning a dataframe if show=True
def run(query, cnx, show=False):

    # Instantiates a cursor that allows executing SQL statements
    # returning the result as a list of dictionaries   
    cursor = cnx.cursor(buffered=True, dictionary=True)
        
    # Executes the query
    cursor.execute(query)

    # Reports a commit to the database
    cnx.commit()

    # The 'show' parameter defines whether or not the query result is displayed
    if show:

        # Gets the query result as a dataframe
        query_result = DataFrame(cursor.fetchall())

        return query_result

# Gets the registration of connected users
def get_registration(cnx):

    # Extracts login from connected users
    login = cnx.user

    # Should return the registration of a connected user
    query = f'SELECT registration FROM users WHERE login="{login}"'

    return run(query, cnx, show=True).loc[0][0]


# 'acess' defines the access level, being 'admin', 'librarian' or 'user'
# being the key to validate the use of certain operations      
def get_user_acess(login, cnx):        

    # Performs a search on the users table, returning the 'acess' of the
    # logged in user
    query = f'SELECT acess FROM users WHERE login="{login}"'

    acess = run(query, cnx, show=True).loc[0][0]

    return acess


# Add a new user to the database
def register_user(login, password, cnx, acess='user', user_data={}):
    if acess == 'user':
        query = f"DROP USER IF EXISTS '{login}'@'%';"\
                f"CREATE USER '{login}'@'%' IDENTIFIED BY '1234';" \
                f"GRANT SELECT ON `college_library_db`.`users` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books` TO '{login}'@'%';" \
                f"GRANT SELECT, INSERT ON `college_library_db`.`book_reservations` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`book_borrowings` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_category` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_publisher` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_release` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_author` TO '{login}'@'%';" \
                f"GRANT EXECUTE ON FUNCTION `college_library_db`.`get_user_acess` TO '{login}'@'%';" \
                f"FLUSH PRIVILEGES;" \
                f"INSERT INTO users (login, password, acess) VALUES ('{login}', '{password}', '{user_data['registration']}');"

        if user_data['user_type'] == 'student':
            query += "INSERT INTO students (registration, name, entry_date, expected_completion_date, adress, course_code)" \
                    f"VALUES ('{user_data['registration']}', '{user_data['name']}', '{user_data['entry_date']}'," \
                    f"'{user_data['expected_completion_date']}', '{user_data['adress']}', '{user_data['course_code']}');"

        elif user_data['user_type'] == 'employee':
            query += "INSERT INTO employees (registration, name, adress)" \
                    f"VALUES ('{user_data['registration']}', '{user_data['name']}', '{user_data['adress']}');"                    

        if user_data['user_type'] == 'professor':
            query += "INSERT INTO professors (registration, name, hiring_date, work_regime, adress, cell_phone, course_code)" \
                    f"VALUES ('{user_data['registration']}', '{user_data['name']}', '{user_data['hiring_date']}'," \
                    f"'{user_data['work_regime']}', '{user_data['adress']}', '{user_data['cell_phone']}', '{user_data['course_code']}');"

    elif acess == 'librarian':
        query = f"DROP USER IF EXISTS '{login}'@'%';" \
                f"DROP USER IF EXISTS '{login}'@'%';" \
                f"CREATE USER '{login}'@'%' IDENTIFIED BY '1234';" \
                f"GRANT SELECT ON `college_library_db`.`books` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`users` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`students` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`employees` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_category` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_publisher` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_release` TO '{login}'@'%';" \
                f"GRANT SELECT ON `college_library_db`.`books_by_author` TO '{login}'@'%';" \
                f"GRANT SELECT, INSERT, DELETE, UPDATE ON `college_library_db`.`book_reservations` TO '{login}'@'%';" \
                f"GRANT SELECT, INSERT, DELETE, UPDATE ON `college_library_db`.`book_borrowings` TO '{login}'@'%';" \
                f"FLUSH PRIVILEGES;" \
                f"INSERT INTO users (login, password, acess) VALUES ('{login}', '{password}', '{acess}');"

    elif acess == 'admin':
        query = f"DROP USER IF EXISTS '{login}'@'%';" \
                f"CREATE USER '{login}'@'%' IDENTIFIED BY '{password}';" \
                f"GRANT ALL ON `college_library_db`.* TO '{login}'@'%';" \
                 "FLUSH PRIVILEGES;" \
                f"INSERT INTO users (login, password, acess) VALUES ('{login}', '{password}', '{acess}');"
    


    run(query, cnx)  # Executes the query


# Removes a given user from the database
def delete_user(login, cnx):
    
    query = f'DELETE FROM users WHERE login={login};DROP USER {login}'

    return run(query, cnx)

# Gets the registration of the connected user
def get_user_type(cnx):

    # Extracts the registrarion from connected user
    registration = get_registration(cnx)

    # If the registration exists, returns "student"|"professor"|"employee"|"none"
    query = f'SELECT @get_user_type({registration})'
    
    return run(query, cnx, show=True).loc[0][0]


# Authorizes the borrow of a book that is reserved
def borrow_book(registration, isbn_code, cnx):

    # Receives the borrow confirmation date to calculate the devolution date
    today = datetime.today().strptime(today, "%Y-%m-%d")
    
    # Extracts the type from the logged in user: "student"|"professor"|"employee"|"none"
    user_type = get_user_type(cnx)

    # Based on the user category, performs the insertion
    if user_type == 'student':
        devolution_date = today + datetime.timedelta(days=15)
        query = f'INSERT INTO book_borrowings (devolution_date, registration, isbn_code) ' \
                f'VALUES ("{devolution_date}", "{registration}", "{isbn_code}")'

    elif user_type == 'employee':
        devolution_date = today + datetime.timedelta(days=21)
        query = f'INSERT INTO book_borrowings (devolution_date, registration, isbn_code) ' \
                f'VALUES ("{devolution_date}", "{registration}", "{isbn_code}")'

    elif user_type == 'professor':
        devolution_date = today + datetime.timedelta(days=30)
        query = f'INSERT INTO book_borrowings (devolution_date, registration, isbn_code) ' \
                f'VALUES ("{devolution_date}", "{registration}", "{isbn_code}")'

    # If the user is not from any type, the thread is terminated returning False
    elif user_type == 'none':
        return False

    run(query, cnx)


# Reserves the selected book
def reserve_book(isbn_code, cnx):

    # Extracts the registrarion from connected user
    registration = get_registration(cnx)

    query = 'INSERT INTO book_reservations (registration, isbn_code) ' \
           f'VALUES ("{registration}", "{isbn_code}")'

    run(query, cnx)


# Removes a book from the borrowed books table
def return_book(registration, isbn_code, cnx):

    query = f'DELETE FROM book_borrowings WHERE isbn_code="{isbn_code}" AND registration={registration}'

    run(query, cnx)
    

# Returns a dataframe with the books searched
def get_books(title, filter, cnx):

    # Search all books given a title
    if filter == '1':
        query = f"SELECT * FROM books WHERE title LIKE '%{title}%'"

    # Search books based on category
    elif filter == '2':        
        query = f"SELECT * FROM books_by_category WHERE title LIKE '%{title}%'"

    # Search books based on publisher
    elif filter == '3':        
        query = f"SELECT * FROM books_by_publisher WHERE title LIKE '%{title}%'"        

    # Search books based on release year
    elif filter == '4':        
        query = f"SELECT * FROM books_by_release WHERE title LIKE '%{title}%'"        

    # Search books based on author
    elif filter == '5':        
        query = f"SELECT * FROM books_by_author WHERE title LIKE '%{title}%'"        
    
    return run(query, cnx, show=True)

# Returns the list of the connected user reserved books
def user_reserved_books(cnx):

    # Extracts the registrarion from connected user
    registration = get_registration(cnx)

    query = 'SELECT books.title, books.isbn_code, reservation_date ' \
            'FROM book_reservations JOIN books ' \
            'ON book_reservations.isbn_code = books.isbn_code ' \
           f'WHERE registration = "{registration}"'

    reservations = run(query, cnx, show=True)

    if reservations.empty:
        return "You don't have any reservations yet."
    
    else:
        return reservations


# Returns the list of the connected user borrowed books
def get_user_borrowed_books(cnx):

    # Extracts the registrarion from connected user
    registration = get_registration(cnx)

    query = 'SELECT books.title, borrow_date, devolution_date, books.isbn_code ' \
            'FROM book_borrowings JOIN books ' \
            'ON book_borrowings.isbn_code = books.isbn_code ' \
           f'WHERE registration={registration}'    

    user_borrowed_books = run(query, cnx, show=True)    
    
    if user_borrowed_books.empty:
        return "You don't have any borrowed books yet."
    
    return user_borrowed_books
        


# Returns a dataframe with all users with the specified name
def get_user(login, cnx):

    query = f'SELECT * FROM users WHERE login = "{login}"'        

    users = run(query, cnx, show=True)

    return users


# Returns a dataframe with all borrow requests for
# a user with the specified registration number
def get_reservations(registration, cnx):
    
    query = f'SELECT * FROM book_reservations WHERE registration="{registration}"'

    reservations = run(query, cnx, show=True)

    return reservations
        


# Returns a dataframe containing all borrowed books
def get_borrowed_books(cnx):

    query = f'SELECT * FROM book_borrowings'

    borrowed_books = run(query, cnx, show=True)

    if borrowed_books.empty:
        return 'There are no borrowings at the moment.'

    else:
        return borrowed_books
