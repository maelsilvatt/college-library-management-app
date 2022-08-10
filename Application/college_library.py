# Imports the module with all the screens used in the app
import screens

# Main function responsible for user interaction
# OBS: For the correct functioning of the program, the database
# 'college_library_db' must be active.
def main():
    while True:
        # Interface for connecting to the database
        cnx_data = screens.login() # Returns False or the tuple (user_acess, cnx, login)

        # Prevents the program from progressing if the data is incorrect
        if cnx_data == 'error':

            # Closes the main program
            return

        else:
            (user_acess, cnx) = cnx_data

        # Interface for common users
        if user_acess == 'user':
            screens.user_menu(cnx)

        # Interface for librarians
        elif user_acess == "librarian":
            screens.librarian_menu(cnx)

        # Interface for admins
        elif user_acess == 'admin':
            screens.admin_menu(cnx)

if __name__ == '__main__':
    main()