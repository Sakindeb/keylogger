import os.path

def checkExistence():
    if os.path.exists("info.txt"):
        pass
    else:
        file = open("info.txt", 'w')
        file.close()

# Write to File
def appendNew():
    userName = input("Please enter the user name: ")
    password = input("Please enter the password here: ")
    website = input("Please enter the website address here: ")

    with open("info.txt", 'a') as file:
        file.write("---------------------------------\n")
        file.write("UserName:" + userName + "\n")
        file.write("Password:" + password + "\n")
        file.write("Website:" + website + "\n")
        file.write("--------------------\n")

# Output the Password
def readPasswords():
    with open('info.txt', 'r') as file:
        content = file.read()
        print(content)

# Main function
if __name__ == "__main__":
    checkExistence()
    appendNew()
    readPasswords()
