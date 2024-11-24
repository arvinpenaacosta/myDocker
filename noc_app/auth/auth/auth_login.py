from authentication import authenticate  # Import the authenticate function
#import getpass
import pwinput as pin

# Prompt the user for their credentials
username = input("Enter your username (e.g., user1): ")

#password = getpass.getpass("Enter your password: ")
password = pin.pwinput(prompt = 'Enter your password: ', mask='#')


# Call the authenticate function and check the result
if authenticate(username, password):
    print("Login successful")
else:
    print("Login failed")
