from ldap3 import Server, Connection, ALL

# LDAP server details
LDAP_SERVER = "ldap://winserver2022.devapp.local:389"

# User credentials to test
LDAP_USER1 = "user1@devapp.local"
LDAP_PASSWORD1 = "!@#$1qaZ"

try:
    # Set up the server and connection
    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, user=LDAP_USER1, password=LDAP_PASSWORD1)

    # Attempt to bind with user credentials
    if conn.bind():
        print("Login successful")
    else:
        #print("Login failed:", conn.result)
        print("Login failed:")
    # Unbind connection after the operation
    conn.unbind()

except Exception as e:
    print(f"LDAP bind failed: {e}")

