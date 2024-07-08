import pymysql
from config import DB_CONFIG
import json

def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG["HOST"],
        user=DB_CONFIG["USER"],
        password=DB_CONFIG["PASSWORD"],
        database=DB_CONFIG["DATABASE"],
        port=DB_CONFIG["PORT"]
    )

def fetch_email():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Email FROM auth")
    output = cur.fetchall()
    conn.close()
    return [i[0] for i in output]

def recover_passkey(new_password, email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE auth SET Password = %s WHERE Email = %s", (new_password, email))
    conn.commit()
    conn.close()

def fetch_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Email, Password FROM auth")
    output = cur.fetchall()
    conn.close()
    return output
def Profile_build_main(OrgName,Gender,Post):
    conn=get_db_connection
    cur=conn.cursor()
    cur.execute("INSERT INTO auth (OrgName,Gender,OrgPost) VALUES (%s, %s, %s, %s, %s)",
                (OrgName,Gender,Post))
    cur.commit()
    conn.close()

def data_post():
    conn = get_db_connection()
    cur=conn.cursor()
    f=open("test.json","r+")
    data=json.load(f)
    data_list=list(data.values())
    DEVICE_ID=data_list[0]
    print(data_list)
    placeholders = ', '.join(['%s'] * len(data_list))
    insert_query = f"INSERT INTO DEVICE_DATA (D_ID, SSL_ID, GIS, PV, PC, PP, BV, BC, BP, LV, LC, LP, SSt, BF, MF, LF, LSt, BrL, HEn, BCPr, BDPr, BTem, GPSP) VALUES ({placeholders})"
    cur.execute(insert_query,data_list)
    f.truncate(0)
    f.close()
    select_query =f"SELECT * FROM DEVICE_DATA WHERE {DEVICE_ID}=D_ID"
    cur.execute(select_query)
    output = cur.fetchall()
    print(output)
    main=open("repo.json","ab+")
    json.dump(output)
    main.close()
    conn.commit()
    conn.close()