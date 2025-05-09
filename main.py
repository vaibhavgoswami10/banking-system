import random
import mysql.connector
from decimal import Decimal
from datetime import datetime
import re

# Database setup
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vaibhav@12345",
    database="banking_system"
)
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    account_number VARCHAR(10) UNIQUE,
    dob DATE,
    city VARCHAR(255),
    password VARCHAR(255),
    balance DECIMAL(10, 2),
    contact_number VARCHAR(10),
    email VARCHAR(255),
    address TEXT,
    active TINYINT DEFAULT 1
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_number VARCHAR(10),
    type VARCHAR(50),
    amount DECIMAL(10, 2),
    date DATETIME
)''')

connection.commit()

def validate_contact(contact):
    return re.match(r"^\d{10}$", contact)

def generate_account_number():
    return str(random.randint(1000000000, 9999999999))

def validate_password(password):
    return (len(password) >= 8 and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '!@#$%^&*()-_+=' for c in password))

def validate_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

def update_profile(user_data):
    print("Updating profile...")
    new_name = input(f"Enter new name (Current: {user_data[1]}): ") or user_data[1]
    new_city = input(f"Enter new city (Current: {user_data[4]}): ") or user_data[4]
    new_contact = input(f"Enter new contact number (Current: {user_data[6]}): ") or user_data[6]
    while not validate_contact(new_contact):
        print("Invalid contact number. It must contain 10 digits.")
        new_contact = input("Enter contact number: ")
    
    new_email = input(f"Enter new email (Current: {user_data[7]}): ") or user_data[7]
    while not validate_email(new_email):
        print("Invalid email address.")
        new_email = input("Enter email ID: ")
    
    new_address = input(f"Enter new address (Current: {user_data[8]}): ") or user_data[8]

    cursor.execute('''UPDATE users SET name = %s, city = %s, contact_number = %s, email = %s, address = %s 
                 WHERE account_number = %s''',
              (new_name, new_city, new_contact, new_email, new_address, user_data[2]))
    connection.commit()
    print("Profile updated successfully.")

def toggle_account_status(user_account):
    if user_account[9] == 1:
        cursor.execute("UPDATE users SET active = 0 WHERE account_number = %s", (user_account[2],))
        print("Account deactivated.")
    else:
        cursor.execute("UPDATE users SET active = 1 WHERE account_number = %s", (user_account[2],))
        print("Account activated.")
    connection.commit()

def display_all_users():
    cursor.execute("SELECT * FROM users")
    records = cursor.fetchall()
    if records:
        for record in records:
            print(f"ID: {record[0]}\nName: {record[1]}\nAccount Number: {record[2]}\nDOB: {record[3]}\nCity: {record[4]}\nBalance: {record[5]}\nContact: {record[6]}\nEmail: {record[7]}\nAddress: {record[8]}\nActive: {'Yes' if record[9] else 'No'}\n")
    else:
        print("No users found.")

def perform_transfer(sender_account):
    amount = float(input("Enter amount to transfer: "))
    if Decimal(amount) > Decimal(sender_account[6]):
        print("Insufficient balance.")
    else:
        receiver_account_number = input("Enter receiver's account number: ")
        cursor.execute("SELECT * FROM users WHERE account_number = %s", (receiver_account_number,))
        receiver_account = cursor.fetchone()

        if receiver_account:
            updated_sender_balance = Decimal(sender_account[6]) - Decimal(amount)
            updated_receiver_balance = Decimal(receiver_account[6]) + Decimal(amount)
            cursor.execute("UPDATE users SET balance = %s WHERE account_number = %s", (updated_sender_balance, sender_account[2]))
            cursor.execute("UPDATE users SET balance = %s WHERE account_number = %s", (updated_receiver_balance, receiver_account_number))
            cursor.execute("INSERT INTO transactions (account_number, type, amount, date) VALUES (%s, 'Debit', %s, %s)",
                      (sender_account[2], amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            cursor.execute("INSERT INTO transactions (account_number, type, amount, date) VALUES (%s, 'Credit', %s, %s)",
                      (receiver_account_number, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            connection.commit()
            print("Transfer successful.")
        else:
            print("Receiver account not found.")

def update_password(user_account):
    current_password = input("Enter your old password: ")
    if current_password == user_account[5]:
        new_password = input("Enter your new password: ")
        while not validate_password(new_password):
            print("Password must be at least 8 characters long, include an uppercase letter, a number, and a special character.")
            new_password = input("Enter new password: ")
        cursor.execute("UPDATE users SET password = %s WHERE account_number = %s", (new_password, user_account[2]))
        connection.commit()
        print("Password changed successfully.")
    else:
        print("Old password is incorrect.")

def register_new_user():
    name = input("Enter name: ")
    dob = input("Enter date of birth (YYYY-MM-DD): ")
    city = input("Enter city: ")
    password = input("Enter password: ")

    while not validate_password(password):
        print("Password must be at least 8 characters long, include an uppercase letter, a number, and a special character.")
        password = input("Enter password: ")

    balance = float(input("Enter initial balance (minimum 2000): "))
    while balance < 2000:
        print("Initial balance must be at least 2000.")
        balance = float(input("Enter initial balance (minimum 2000): "))

    contact_number = input("Enter contact number: ")
    while not validate_contact(contact_number):
        print("Invalid contact number. It must contain 10 digits.")
        contact_number = input("Enter contact number: ")

    email = input("Enter email ID: ")
    while not validate_email(email):
        print("Invalid email address.")
        email = input("Enter email ID: ")

    address = input("Enter address: ")

    account_number = generate_account_number()

    try:
        cursor.execute('''INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email, address)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                  (name, account_number, dob, city, password, balance, contact_number, email, address))
        connection.commit()
        print(f"User added successfully. Account Number: {account_number}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def user_authentication():
    account_number = input("Enter account number: ")
    password = input("Enter password: ")

    cursor.execute("SELECT * FROM users WHERE account_number = %s AND password = %s", (account_number, password))
    user_record = cursor.fetchone()

    if user_record:
        print("Login successful!")
        while True:
            print("\n1. View Balance\n2. View Transactions\n3. Credit Amount\n4. Debit Amount\n5. Transfer\n6. Toggle Account Status\n7. Change Password\n8. Update Profile\n9. Logout")
            choice = int(input("Enter your choice: "))

            if choice == 1:
                print(f"Current Balance: {user_record[6]}")
            elif choice == 2:
                cursor.execute("SELECT * FROM transactions WHERE account_number = %s", (account_number,))
                transaction_logs = cursor.fetchall()
                for log in transaction_logs:
                    print(f"Type: {log[2]}, Amount: {log[3]}, Date: {log[4]}")
            elif choice == 3:
                credit_amount = float(input("Enter amount to credit: "))
                updated_balance = Decimal(user_record[6]) + Decimal(credit_amount)
                cursor.execute("UPDATE users SET balance = %s WHERE account_number = %s", (updated_balance, account_number))
                cursor.execute("INSERT INTO transactions (account_number, type, amount, date) VALUES (%s, 'Credit', %s, %s)",
                              (account_number, credit_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                connection.commit()
                print("Credit successful.")
            elif choice == 4:
                debit_amount = float(input("Enter amount to debit: "))
                updated_balance = Decimal(user_record[6]) - Decimal(debit_amount)
                if updated_balance < 0:
                    print("Insufficient balance.")
                else:
                    cursor.execute("UPDATE users SET balance = %s WHERE account_number = %s", (updated_balance, account_number))
                    cursor.execute("INSERT INTO transactions (account_number, type, amount, date) VALUES (%s, 'Debit', %s, %s)",
                                  (account_number, debit_amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    connection.commit()
                    print("Debit successful.")
            elif choice == 5:
                perform_transfer(user_record)
            elif choice == 6:
                toggle_account_status(user_record)
            elif choice == 7:
                update_password(user_record)
            elif choice == 8:
                update_profile(user_record)
            elif choice == 9:
                print("Logged out successfully.")
                break
            else:
                print("Invalid choice.")
    else:
        print("Invalid account number or password.")

def main():
    print("Welcome to the Banking System")
    while True:
        print("\n1. Register\n2. User Login\n3. View All Users\n4. Exit")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            register_new_user()
        elif choice == 2:
            user_authentication()
        elif choice == 3:
            display_all_users()
        elif choice == 4:
            print("Exiting the system.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
    # print("What is this")
