import random
import re
import sys
import sqlite3

# Database class to initialise the database
class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    # Method to process the input transaction queries/requests.
    def requests(self, request):
        self.cur.execute(request)
        # If it is a SELECT Query, return the value. Otherwise, only execute.
        if re.search(r'^SELECT .*', request.lstrip(), re.IGNORECASE) is not None:
            return self.cur.fetchone()
        else:
            self.conn.commit()
            return None     
    # Method to close the Database connection
    def close_connection(self):
        self.conn.close()

# Banking class that includes all the banking-related functionalities.
class Banking(Database):

    def __init__(self, db_name, table_name, user_id=0, user_state=0):
        super().__init__(db_name)
        # Name of the Database 
        self.db_name = db_name
        # Name of the table
        self.table_name = table_name
        # User ID will be the same as the Customer Account Number (Number excluding the first 6 digits of the card number)
        self.user_id = user_id
        # User state will be 0 if user is not logged in and 1 if user is logged in
        self.user_state = user_state
        # Dictionary to load the different commands shown in the interface and to associate the corresponding functions that are associated with those functionalities
        self.interface_dict = [
            {'1': ["Create an account", self.account_create], '2': ["Log into account", self.account_login],
             '0': ["Exit", self.exit_func]},
            {'1': ["Balance", self.balance_disp], '2': ["Add Funds", self.add_funds], '3': ["Transfer Funds", self.transfer_funds], '4': ["Close Account", self.delete_account], '5': ["Log Out", self.account_logout], '0': ["Exit", self.exit_func]}]
        # Use the existing table if it is created properly and according to specification or drop and create new one otherwise.
        try:
            request = 'SELECT id,number,pin,balance FROM {0}'.format(self.table_name)
            super().requests(request)
        except:
            super().requests('DROP TABLE IF EXISTS {0}'.format(self.table_name))
            super().requests('''CREATE TABLE {0}(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    number TEXT,
                                    pin TEXT,
                                    balance INTEGER DEFAULT 0
                                    )
                             '''.format(self.table_name))
    
    # Function to display the user interface and navigate to the respective screens.
    def interface_screen(self):
        print()
        for item in self.interface_dict[self.user_state]:
            print("{0}. {1}".format(item, self.interface_dict[self.user_state][item][0]))
        input_key = input()
        try:
            self.interface_dict[self.user_state][str(input_key)][1]()

        except Exception as e:
            print("\nPlease enter a valid input ")            
            self.interface_screen()
    
    # Function to create a new user account.
    def account_create(self):
        customer_account_number = format((random.randint(0, 999999999)), '09d')    
        customer_pin = format((random.randint(0, 9999)), '04d')        
        request = 'SELECT number FROM {0} WHERE number = 400000{1}'.format(self.table_name, customer_account_number)
        while super().requests(request) is not None:
            customer_account_number = format((random.randint(0, 999999999)), '09d')
            request = 'SELECT number FROM {0} WHERE number = 400000{1}'.format(self.table_name, customer_account_number)
        card_number = self.card_no_generator('400000{0}'.format(customer_account_number))
        print("\nYour card has been created \nYour card number: \n{0} \nYour card PIN: \n{1}".format(card_number,
                                                                                                     customer_pin))
        request = "INSERT INTO {0} (number, pin) VALUES ({1}, substr('0000'||{2}, -4, 4))".format(self.table_name, card_number, customer_pin)
        super().requests(request)
    
    # Function to generate a card number checksum using Luhn's Algorithm.
    def card_no_generator(self, customer_account_number):
        if customer_account_number:
            customer_account_number_array = [int(j) if (i + 1) % 2 == 0 else int(j) * 2 for i, j in
                                         enumerate(customer_account_number)]
            customer_account_number_array = [i if i <= 9 else i - 9 for i in customer_account_number_array]
            if sum(customer_account_number_array) % 10 != 0:
                return "{0}{1}".format(customer_account_number, (10 - (sum(customer_account_number_array) % 10)))
            return "{0}0".format(customer_account_number)
        return None

    # Function for provisioning the login of a user.
    def account_login(self):
        print("\nEnter your card number:")
        card_number = str(input())
        print("Enter your PIN:")
        customer_pin = str(input())
        try:
            if customer_pin == super().requests(
                    'SELECT pin FROM {0} WHERE number = {1}'.format(self.table_name, card_number))[0]:
                print("\nYou have successfully logged in!")
                self.user_state = 1
                self.user_id = card_number.split('400000')[1]
            else:
                print("\nWrong card number or PIN!")
        except:
            print("\nWrong card number or PIN!")
    
    # Function for provisioning the logout of a user.
    def account_logout(self):
        self.user_state = 0
        self.user_id = 0
        print("\nYou have successfully logged out!")
    
    # Function to display the account balance of a user.
    def balance_disp(self):
        balance = super().requests(
                    'SELECT balance FROM {0} WHERE number = 400000{1}'.format(self.table_name, self.user_id))[0]
        print("\nBalance: {0}".format(balance))
    
    # Function to add funds to the user's own account
    def add_funds(self):
        balance = super().requests(
                    'SELECT balance FROM {0} WHERE number = 400000{1}'.format(self.table_name, self.user_id))[0]
        print("\nEnter amount: ")
        income = int(input())
        super().requests(
            'UPDATE {0} SET balance = {1} WHERE number = 400000{2}'.format(self.table_name, balance+income, self.user_id))
        print("Amount was added!")
    
    # Function to add funds to a different user's account
    def transfer_funds(self):
        print("\nTransfer")
        balance = super().requests(
                    'SELECT balance FROM {0} WHERE number = 400000{1}'.format(self.table_name, self.user_id))[0]
        print("Enter card number: ")
        receiver_card_no = super().requests(
                    'SELECT number FROM {0} WHERE number = {1}'.format(self.table_name, input()))        
        if receiver_card_no is None:
            print("That account does not exist. Please check the entered Card Number.")        
        elif '400000{0}'.format(self.user_id) == receiver_card_no[0]:
            print("You can't transfer money to the same account!")
        else:
            receiver_balance = super().requests(
                    'SELECT balance FROM {0} WHERE number = {1}'.format(self.table_name, int(receiver_card_no[0])))
            print("Enter how much money you want to transfer: ")
            balance_transfer = int(input())
            if balance_transfer > balance:
                print("Not enough money!")
            else:
                super().requests(
                    'UPDATE {0} SET balance = {1} WHERE number = 400000{2}'.format(self.table_name, balance-balance_transfer, self.user_id))
                super().requests(
                    'UPDATE {0} SET balance = {1} WHERE number = {2}'.format(self.table_name, receiver_balance[0]+balance_transfer, int(receiver_card_no[0])))
                print("Success!")
    
    # Function to delete the user's account when logged in
    def delete_account(self):
        super().requests(
            'DELETE FROM {0} WHERE number = 400000{1}'.format(self.table_name, self.user_id))
        self.user_state = 0
        self.user_id = 0
        print("\nThe account has been closed!")

    # Function to exit the code
    def exit_func(self):    
          super().close_connection()        
          sys.exit()
        
          
# Start of the Program.

if __name__ == '__main__': 
  try:
    user = Banking('card.s3db', 'card')
    while True:
      user.interface_screen()
  except:
    print("\nThe Program has ended. Thank you for using our service.")
