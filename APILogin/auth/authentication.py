from ldap3 import Server, Connection, ALL


# Define LDAP server details and base OU
LDAP_SERVER = "ldap://winserver2022.devapp.local:389"
BASE_OU = "OU=IT_NOC,DC=devapp,DC=local"

def authenticate(username, password):
    """Attempts to authenticate a user within a specific OU."""
    user_dn = f"CN={username},{BASE_OU}"
    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, user=user_dn, password=password)
    if conn.bind():
        conn.unbind()
        return True
    return False
