import database as db
from hashlib import sha256

def hash_password(input_):
    return sha256(input_.encode('utf-8')).hexdigest()

query = "UPDATE Users SET PasswordHash = ? WHERE Username = 'johndoe'"
query2 = "SELECT * FROM Users"
hash = hash_password("1234")
print(hash)
parameters = (hash,)
db.execute_query("shorturls.db", query, commit=True, params=parameters)

print(db.execute_query("shorturls.db", query2))