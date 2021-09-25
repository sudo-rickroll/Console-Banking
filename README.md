# Console Banking

This is a miniature banking application built using Python for front-end and SQLite Database engine library for backend management. It uses Luhn's algorithm to generate  the checksum for the user account.

Download the python file and run it in a console. You will be presented with the following options :

![Welcome screen](https://user-images.githubusercontent.com/65642947/134769140-406d01f6-75e9-45f1-bc56-f54226627ecf.JPG)

Type the appropriate option number and hit Enter. If you create an account, the cad number and PIN will be generated and stored in a local database file. Any number of accounts can be created. You can then login using any of the correct pair of card number and PIN. If you login successfully, you will be presented with the following screen :

![Post-Login](https://user-images.githubusercontent.com/65642947/134769239-3aeb23d6-fd70-4f83-90e9-22712ddab4e1.JPG)

You can then view the balance of the account, add funds to the currently logged-in account, transfer funds from the current logged-in account to any of the accounts that were created at any instance (as it is stored in the same local DB) of application execution, close the account, log out or exit the application.
