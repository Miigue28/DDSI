import oracledb
import tkinter as tk
import csv

# Global Variables
cursor = None
connection = None
window = None
subwindow = None
contador_pedidos :int = 0
table_name = list({"DETALLEPEDIDO", "STOCK", "PEDIDO"})

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

def mostrarContenidoTablas():
    global cursor, table_name
    
    for i in range(3):
        try:
            print(f"{table_name[i]}")
            for r in cursor.execute(f"select * from {table_name[i]}"):
                print(r)
        except:
            print(f"\n[!] Error: La tabla {table_name[i]} no existe")

def crearStock():
    global cursor, table_name
    # Comprobamos que las tablas existen, en dicho caso se destruyen
    #for i in range(3):
    #    try:
    #        cursor.execute(f"DROP TABLE {table_name[i]}")
    #    except:
    #        print(f"\n[!] Error al eliminar tabla {table_name[i]}")
    
    cursor.execute(f"select count(*) from user_tables where table_name = 'DETALLEPEDIDO'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table DETALLEPEDIDO")
    
    cursor.execute(f"select count(*) from user_tables where table_name = 'STOCK'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table STOCK")

    cursor.execute(f"select count(*) from user_tables where table_name = 'PEDIDO'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table PEDIDO")

    # Creamos las tablas necesarias
    cursor.execute("""
        CREATE TABLE STOCK (
            cProducto NUMBER(4) CONSTRAINT código_producto_clave_primaria PRIMARY KEY,
            Nombre VARCHAR(20),
            Cantidad NUMBER(4) CONSTRAINT cantidad_not_null NOT NULL
    )""")
        
    cursor.execute("""
    CREATE TABLE PEDIDO (
        cPedido NUMBER(4) CONSTRAINT código_pedido_clave_primaria PRIMARY KEY,
        cCliente NUMBER(4),
        fechaPedido DATE
    )""")
    
    cursor.execute("""
    CREATE TABLE DETALLEPEDIDO (
        cPedido CONSTRAINT código_pedido_clave_externa_pedido REFERENCES PEDIDO(cPedido),
        cProducto CONSTRAINT código_producto_clave_externa_producto REFERENCES STOCK(cProducto),
        Cantidad NUMBER(4),
        CONSTRAINT clave_primaria_detalle_pedido PRIMARY KEY (cPedido, cProducto)
    )""")

    # Insertamos tuplas en la tabla Stock
    with open("products.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into STOCK values('{row[0]}', '{row[1]}', '{row[2]}')")

def recogerDatos(producto, cantidad):
    global cursor

    # Savepoint previo a crear DetallePedido
    cursor.execute("savepoint DetallePedido")
    
    # Verificar si el código de producto existe
    cursor.execute(f"select count(cProducto) from STOCK where cProducto='{int(producto.get())}'")
    if cursor.fetchone()[0] == 0:
        # Messagebox
        print("\n\n[!] Error: Código de producto no existente\n")

    # Verificar que hay cantidad suficiente del producto
    cursor.execute(f"select Cantidad from STOCK where cProducto = '{int(producto.get())}'")
    if int(cursor.fetchone()[0]) >= int(cantidad.get()):
        cursor.execute(f"insert into DETALLEPEDIDO values({contador_pedidos}, {int(producto.get())}, {int(cantidad.get())})")
        cursor.execute(f"update STOCK set Cantidad = Cantidad - {int(cantidad.get())} where cProducto = {int(producto.get())}")
    else:
        # Messagebox
        print("\n\n[!] Error: Cantidad de producto insuficiente\n") # Se podría gestionar algo mejor esto


def detallePedido():
    global subwindow, contador_pedidos

    # Recogemos la información del pedido
    producto = tk.StringVar(subwindow)
    tk.Label(subwindow, text="Código Producto", justify="center").pack()
    tk.Entry(subwindow, justify="center", textvariable=producto).pack()

    cantidad = tk.StringVar(subwindow)
    tk.Label(subwindow, text="Cantidad", justify="center").pack()
    tk.Entry(subwindow, justify="center", textvariable=cantidad).pack()
    tk.Button(subwindow, text="Añadir Datos", bg="#00A8E8", fg="black", width=10, command=lambda:recogerDatos(producto, cantidad)).pack()
    
    # Mostramos el contenido de la base de datos
    mostrarContenidoTablas()

def eliminarDetallePedido():
    global cursor

    cursor.execute("rollback to DetallePedido")
    # Mostramos el contenido de la base de datos
    mostrarContenidoTablas()

def crearPedido(cliente):
    global cursor, subwindow

    # Insertamos el pedido en su correspondiente tabla
    cursor.execute(f"insert into PEDIDO values ({contador_pedidos}, {int(cliente.get())}, sysdate)")

    # Savepoint previo a crear pedido
    cursor.execute(f"savepoint Pedido")

def cancelarPedido():
    global cursor

    cursor.execute("rollback Pedido")
    # Mostramos el contenido de la base de datos
    mostrarContenidoTablas()

def finalizarPedido():
    global cursor, subwindow

    cursor.execute("commit")

    # Incrementamos el contador de pedidos
    contador_pedidos = contador_pedidos + 1

    # Destruimos la subventana
    subwindow.destroy()

def altaPedido():
    global cursor, window, subwindow, contador_pedidos

    # TODO: Cambiar para usar Frames
    subwindow = tk.Toplevel()
    subwindow.title("Dar de Alta Pedido")
    subwindow.geometry("800x800")
    subwindow.configure(background="white")

    tk.Label(subwindow, text="Dar de Alta Pedido", bg="#00A8E8", fg="black", font=("Arial", 16)).pack()

    # Introducir código de cliente
    cliente = tk.StringVar(subwindow)
    tk.Label(subwindow, text="Código Cliente", justify="center").pack()
    tk.Entry(subwindow, justify="center", textvariable=cliente).pack()

    # Botones del menú
    tk.Button(subwindow, text="Añadir cliente", bg="#00A8E8", fg="black", width=10, command=lambda:crearPedido(cliente)).pack()
    tk.Button(subwindow, text="Añadir detalle de producto", bg="#00A8E8", fg="black", width=40, command=detallePedido).pack()
    tk.Button(subwindow, text="Eliminar todos los detalles de producto", bg="#00A8E8", fg="black",width=40, command=eliminarDetallePedido).pack()
    tk.Button(subwindow, text="Cancelar Pedido", bg="#00A8E8", fg="black", width=40, command=cancelarPedido).pack()
    tk.Button(subwindow, text="Finalizar Pedido", bg="#00A8E8", fg="black", width=40, command=finalizarPedido).pack()
    

def salir():
    global window

    # Cerramos la conexión
    db_close()

    # Destruimos la ventana
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
    titulo = tk.Label(window, text="Menú Principal", bg="#00A8E8", fg="black", font=("Arial", 16))
    titulo.pack()

    # Botones del menú
    tk.Button(window, text="Crear Stock", bg="#00A8E8", fg="black", width=40, command=crearStock).pack()
    tk.Button(window, text="Dar de Alta Pedido", bg="#00A8E8", fg="black", width=40, command=altaPedido).pack()
    tk.Button(window, text="Mostrar Contenido Tablas", bg="#00A8E8", fg="black", width=40, command=mostrarContenidoTablas).pack()
    tk.Button(window, text="Salir", bg="#00A8E8", fg="black", width=40, command=salir).pack()

    # Ejecutar la ventana
    window.mainloop()

if __name__ == "__main__":
    main()
