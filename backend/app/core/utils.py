from passlib.context import CryptContext 

# Defining Hashing Algorithm 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing the password 
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Verifying the Password
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)