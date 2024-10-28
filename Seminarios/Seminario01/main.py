import oracledb
import tkinter as tk
import csv

# Global Variables
cursor = None
connection = None
window = None

def db_connect():
    global connection, cursor
    try:
        cp = oracledb.ConnectParams(user="x0070272", password="x0070272", host="oracle0.ugr.es", port=1521, service_name="practbd")
        connection = oracledb.connect(params=cp)
        cursor = connection.cursor()
    except Exception as e:
        print(f"\n\n[!] Error connecting to the database\n {e}")
        exit(1)

def db_close():
    global connection, cursor
    cursor.close()
    connection.close()

def createStock():
    global cursor
    # Comprobamos que las tablas existen, en dicho caso se destruyen
    #table_name = list({"DetallePedido", "Stock", "Pedido"})
    #for i in range(3):
    #    cursor.execute(f"select count(*) from user_tables where table_name='{table_name[i]}'")
    #    exists = cursor.fetchone()[0]
    #    print(f"Existe la tabla {table_name[i]}?: {exists}")
    #    if (exists > 0):
    #        print(f"Eliminando tabla {table_name[i]}")
    #        cursor.execute(f"drop table {table_name[i]}")

    # Creamos las tablas necesarias
    cursor.execute("drop table DetallePedido")
    cursor.execute("drop table Stock")
    cursor.execute("create table Stock(cProducto integer PRIMARY KEY, Nombre varchar(20), Cantidad integer)")
    #cursor.execute("create table Pedido(cPedido integer PRIMARY KEY, cCliente integer, FechaPedido Date)")
    #cursor.execute("create table DetallePedido(cPedido REFERENCES Pedido(cPedido), cProducto REFERENCES Stock(cProducto), Cantidad integer, PRIMARY KEY (cPedido, cProducto))")
    #
    ## Insertamos tuplas en la tabla Stock
    #with open("products.csv", "r") as file:
    #    reader = csv.reader(file)
    #    for row in reader:
    #        cursor.execute(f"insert into Stock values('{row[0]}', '{row[1]}', '{row[2]}')")


#def dar_alta_pedido():

    
def mostrar_tablas():
    global cursor

    for r in cursor.execute("select * from Stock"):
        print(r)

    
def salir():
    global window
    db_close()
    window.destroy()

def main():
    db_connect()

    global window
    # Configuración de la ventana principal
    window = tk.Tk()
    window.title("Menú Principal")
    window.geometry("800x800")

    # Etiqueta de título
    titulo = tk.Label(window, text="Menú Principal", font=("Arial", 16))
    titulo.pack(pady=20)

    # Botones del menú
    boton_crear_stock = tk.Button(window, text="Crear Stock", width=20, command=createStock)
    boton_crear_stock.pack(pady=5)

    boton_dar_alta_pedido = tk.Button(window, text="Dar de Alta Pedido", width=20)
    boton_dar_alta_pedido.pack(pady=5)

    boton_mostrar_tablas = tk.Button(window, text="Mostrar Tablas", width=20, command=mostrar_tablas)
    boton_mostrar_tablas.pack(pady=5)

    boton_salir = tk.Button(window, text="Salir", width=20, command=salir)
    boton_salir.pack(pady=5)

    # Ejecutar la ventana
    window.mainloop()

if __name__ == "__main__":
    main()
