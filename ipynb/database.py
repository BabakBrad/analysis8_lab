import sqlite3
import getpass
from ui import *

max_input_try = 3

company_db_name = 'mycompany.db'
staff_tb_name = 'staff'
users_tb_name = 'users'

class db:
    def __init__(self, db_name, staff_table_name, users_table_name):
        self.db_name = db_name
        self.staff_table_name = staff_table_name
        self.users_table_name = users_table_name

        self.loggedin = 0
        self.loggedin_user = None
        self.admin_is_loggedin = 0

        self.reset()

    def reset(self):
        self.conn = sqlite3.connect(self.db_name) 
        self.cur = self.conn.cursor()

        # create staff table if it does not exist
        tb_create = "CREATE TABLE staff (person_id int, lastname CHAR)"
        try:
            self.cur.execute(tb_create)
            # add records to the db manually
            self.cur.execute("INSERT INTO staff (person_id, lastname) VALUES (1, 'Mike')")
            self.cur.execute("INSERT INTO staff (person_id, lastname) VALUES (2, 'Anne')")
            self.conn.commit()
        except: 
            None

        # create user table if it does not exist
        tb_create = "CREATE TABLE users (username TEXT, password TEXT, name TEXT, admin INT);"
        try:
            self.cur.execute(tb_create)
            # add records to the db manually
            self.cur.execute("INSERT INTO users (username, password, name, admin) VALUES ('bob', 123, 'bob', 1)")
            self.cur.execute("INSERT INTO users (username, password, name, admin) VALUES ('mike', 123 , 'mike', 0)")
            self.conn.commit()
        except: 
            None
 
    def add_new_staff(self):
        lastname = input("please enter the staff name: ")

        tb_all = "SELECT * FROM " + self.staff_table_name
        self.cur.execute(tb_all)
        rows = self.cur.fetchall()
        number_of_rows_in_table = len(rows)
        sql_statement = "INSERT INTO staff (person_id, lastname) VALUES ("\
            + str(number_of_rows_in_table + 1) + ", '" + lastname + "') "
        
        self.cur.execute(sql_statement)
        self.conn.commit()
    
    def add_new_user(self):
        if not self.admin_is_loggedin:
            print('Sorry, only admin users are allowed to add new users!')
            return
        username = input('Choose a user name: ')
        
        found = False
        number_of_try = 1
        while not found and number_of_try <= max_input_try:
            user_find = "SELECT * FROM " + self.users_table_name + " WHERE username='" + username + "'"
            self.cur.execute(user_find)
            if self.cur.fetchall():
                print("this user name is already selected by another user.")
                print("please try another user name")
                print()
                number_of_try += 1
            else:
                found = True
        if number_of_try > 3:
            print('no more try is allowed!')
            return

        pw = getpass.getpass()
        pw_repeat = getpass.getpass()
        found = False
        number_of_try = 1
        while pw != pw_repeat and number_of_try <= max_input_try:
            print('passwords do not match! try again.')
            pw = getpass.getpass()
            pw_repeat = getpass.getpass()
            number_of_try += 1
        if number_of_try > 3:
            print('no more try is allowed!')
            return        
        
        # new_user.username = username
        # new_user.password = pw
        # new_user.name = input('enter your name:')
        # new_user.admin = False
        user_temp = [None, None, None, None]
        user_temp[0] = username
        user_temp[1] = pw
        user_temp[2] = input('enter your name:')
        user_temp[3] = False        
        new_user = user(user_temp)

        sql_statement = "INSERT INTO users (username, password, name, admin) VALUES ('"\
            + new_user.username + "', '" + new_user.password + "', '" + new_user.name\
                + "'," + str(int(new_user.admin)) + ")"
        self.cur.execute(sql_statement)
        self.conn.commit()   
        print('New user is successfully added to the database.')     

    def showall_staff(self):
        tb_all = "SELECT * FROM " + self.staff_table_name
        self.cur.execute(tb_all)
        rows = self.cur.fetchall()
        print(rows)

    def login(self):
        username = input("please enter username: ")
        password = getpass.getpass()

        sql_statement = f"SELECT * from users WHERE username='{username}' AND password='{password}'"
        #sql_statement = f'SELECT * from users WHERE username="{username}" AND password="{password}"'
        
        self.cur.execute(sql_statement)

        # try:
        #     self.cur.execute(sql_statement)
        # except OperationalError:
        #     pass    

        loggedin_user = self.cur.fetchone()
        if not loggedin_user:  # An empty result evaluates to False.
            print("Login failed")
        else:
            self.loggedin = 1
            self.loggedin_user = username
            self.admin_is_loggedin = loggedin_user[3]
            print('\nWelcome')
            print('--------------------\n')
            heading = 'Username: ' + self.loggedin_user + '\n' +\
                'Admin: ' + str(bool(self.admin_is_loggedin))
            db_interface = user_interface(heading, db_menu)
            db_interface.run()
        
    def logout(self):
        self.loggedin = 0
        self.loggedin_user = None
        self.admin_is_loggedin = 0
        return 0

    def close(self):
        self.conn.close()

    def not_implemented(self):
        print('Not implemented')

class user:
    def __init__(self, user_data):
        self.username = user_data[0]
        self.password = user_data[1]
        self.name = user_data[2]
        self.admin = user_data[3]

staff = db(company_db_name, staff_tb_name, users_tb_name)
main_menu = [[1, 'login', staff.login ], [0, 'Exit', staff.close]]

db_menu = [ [1, 'add new staff', staff.add_new_staff], [2, 'show all staff', staff.showall_staff],\
            [3, 'add new user', staff.add_new_user], [4, 'change password', staff.not_implemented],\
            [5, 'logout', staff.logout]]