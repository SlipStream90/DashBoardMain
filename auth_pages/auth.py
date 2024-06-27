import pymysql as sql
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash



HOST = "tib.cvywu8ws0g6h.eu-north-1.rds.amazonaws.com"
USER = 'admin'
PASSWORD = "Shanu0921"
DB= 'api_testing'
PORT=3306

"""HOST = "n1nlmysql29plsk.secureserver.net"
USER = 'Tibei_Team'
PASSWORD = "Ow0i*7q75"
DB= 'prog_tool_tibei'
PORT=3306"""



class Auth:
    def __init__(self) :

        self.connection= sql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
        db=DB
        )
        

    def hash_password(self,password):
            hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
            return hash_and_salted_password
      

    def store_credentials(self,f_name,l_name,email,password,contact): #On registering 
        """Store the user's credentials in the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO auth (first_name,last_name,Email,Password,Contact) VALUES (%s,%s,%s,%s,%s)",(f_name,l_name,email,password,contact))
            self.connection.commit()
            print("Credentials stored successfully.")
            self.connection.close()

        except Exception as e:
            print(e)
    def get_username(self):
        try:
            cursor = self.connection.cursor()
            query = "select Email,Password from auth"
            
            cursor.execute(query)
            result = cursor.fetchall()
            self.connection.commit()
            
        except Exception as e:
            print(f"Error storing credentials: {e}")
        finally:
            cursor.close()
            self.connection.close()   
        return result       



   



