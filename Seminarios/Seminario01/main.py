import oracledb
import tkinter as tk
import csv
import sys

# Global Variables
cursor = None
connection = None
window = None
subwindow = None
count :int = 0
table_name = list({"DetallePedido", "Stock", "Pedido"})

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

def mostrar_tablas():
    global cursor, table_name
    
    for i in range(3):
        print(f"{table_name[i]}")
        for r in cursor.execute("select * from {table_name[i]}"):
            print(r)

def createStock():
    global cursor, table_name
    # Comprobamos que las tablas existen, en dicho caso se destruyen
    for i in range(3):
        cursor.execute(f"BEGIN EXECUTE IMMEDIATE 'DROP TABLE {table_name[i]}'; EXCEPTION WHEN OTHERS THEN NULL; END;")

    #cursor.execute(f"select count(*) from user_tables where table_name='DetallePedido'")
    #print(f"Tabla DetallePedido: {cursor.fetchone()[0]}")
    #cursor.execute(f"select count(*) from user_tables where table_name = 'Stock'")
    #print(f"Tabla Stock: {cursor.fetchone()[0]}")
    #cursor.execute(f"select count(*) from user_tables where table_name='Pedido'")
    #print(f"Tabla Pedido: {cursor.fetchone()[0]}")
    
    # Creamos las tablas necesarias
    cursor.execute("create table Stock(cProducto integer PRIMARY KEY, Nombre varchar(20), Cantidad integer)")
    cursor.execute("create table Pedido(cPedido integer PRIMARY KEY, cCliente integer, FechaPedido Date)")
    cursor.execute("create table DetallePedido(cPedido REFERENCES Pedido(cPedido), cProducto REFERENCES Stock(cProducto), Cantidad integer, PRIMARY KEY (cPedido, cProducto))")
    
    # Insertamos tuplas en la tabla Stock
    with open("products.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Stock values('{row[0]}', '{row[1]}', '{row[2]}')")

def productDetails():
    global subwindow, count

    codprod = tk.StringVar(subwindow)
    tk.Label(subwindow, text="Código Producto", justify="center").pack()
    tk.Entry(subwindow, justify="center", textvariable=codprod).pack()

    cantidad = tk.StringVar(subwindow)
    tk.Label(subwindow, text="Cantidad", justify="center").pack()
    tk.Entry(subwindow, justify="center", textvariable=cantidad).pack()
    # TODO: Verificar si el código de producto existe
    # TODO: Averiguar cómo poder guardar los campos en variables
    cursor.execute(f"select Cantidad from Stock where cProducto = '{int(codprod.get())}'")
    if cursor.fectchone()[0] >= int(cantidad.get()):
        cursor.execute(f"insert into DetallePedido values({count}, {int(codprod.get())}, {int(cantidad.get())})")
        cursor.execute(f"update Stock set Cantidad = Cantidad - {int(cantidad.get())} where cProducto = {int(codprod.get())}")
    # TODO: Hacer algo cuando no haya suficiente stock
    

    
def dar_alta_pedido():
    global cursor, window, subwindow, count

    #window.pack_forget()
    subwindow = tk.Toplevel()
    subwindow.geometry("800x800")
    subwindow.configure(background="white")

    title = tk.Label(subwindow, text="Dar de Alta Pedido", font=("Arial", 16)).pack()
    
    tk.Label(subwindow, text="Código Cliente", justify="center").pack()
    nombre_cliente = tk.Entry(subwindow, justify="center").pack()

    # Botones del menú
    tk.Button(subwindow, text="Añadir detalle de producto", bg="#00A8E8", fg="black", width=40).pack()
    tk.Button(subwindow, text="Eliminar todos los detalles de producto", bg="#00A8E8", fg="black",width=40).pack()
    tk.Button(subwindow, text="Cancelar Pedido",  width=40).pack()
    tk.Button(subwindow, text="Finalizar Pedido", width=40).pack()
    

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
    window.configure(background="white")

    # Etiqueta de título
    titulo = tk.Label(window, text="Menú Principal", font=("Arial", 16))
    titulo.pack()

    # Botones del menú
    boton_crear_stock = tk.Button(window, text="Crear Stock", bg="#00A8E8", fg="black", width=20, command=createStock)
    boton_crear_stock.pack()

    boton_dar_alta_pedido = tk.Button(window, text="Dar de Alta Pedido", bg="#00A8E8", fg="black",width=20, command=dar_alta_pedido)
    boton_dar_alta_pedido.pack()

    boton_mostrar_tablas = tk.Button(window, text="Mostrar Tablas",  width=20, command=mostrar_tablas)
    boton_mostrar_tablas.pack()

    boton_salir = tk.Button(window, text="Salir", width=20, command=salir)
    boton_salir.pack()

    # Ejecutar la ventana
    window.mainloop()

if __name__ == "__main__":
    main()
