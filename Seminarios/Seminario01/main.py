import oracledb

def main():
    try:
        cp = oracledb.ConnectParams(user="x0070272", password="x0070272", host="oracle0.ugr.es", port=1521, service_name="practbd")
        connection = oracledb.connect(params=cp)
        cursor = connection.cursor()
    except Exception as e:
        print("\n\n[!] Error connecting to the database\n")
        print(e)
        exit(1)
    else:
        for r in cursor.execute("select sysdate from dual"):
                print(r)
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
