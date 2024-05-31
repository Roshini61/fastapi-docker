from passlib.hash import bcrypt

# Generate bcrypt hashed password
hashed_password = bcrypt.hash("sairam")  #sairam is the input password

print("Hashed Password:", hashed_password)