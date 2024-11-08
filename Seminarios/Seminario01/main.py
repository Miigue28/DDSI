import oracledb
import db_config
import tkinter as tk
import csv
from tkinter import messagebox
from datetime import date

# Global Variables
cursor = None
connection = None
window = None
subwindow = None
clientwindow = None
contador_pedidos :int = 0

def db_connect():
    global connection, cursor
    try:
        cp = oracledb.ConnectParams(user=db_config.user, password=db_config.password, host="oracle0.ugr.es", port=1521, service_name="practbd")
        connection = oracledb.connect(params=cp)
        cursor = connection.cursor()
    except Exception as e:
        messagebox.showerror(title="Conexión", message=f"Error al conectarse a la base de datos")
        exit(1)

def db_close():
    global connection, cursor
    cursor.close()
    connection.close()

def mostrarContenidoTablas():
    global cursor
    
    try:
        print(f"\n---------- DETALLEPEDIDO ----------\n")
        for r in cursor.execute(f"select * from DETALLEPEDIDO"):
            print(f"Pedido: {r[0]},\tProducto: {r[1]},\tCantidad: {r[2]}")
    except:
        messagebox.showerror(message=f"La tabla DETALLEPEDIDO no existe")
    
    try:
        print(f"\n---------- STOCK ----------\n")
        for r in cursor.execute(f"select * from STOCK"):
            print(f"Producto: {r[0]},\tCantidad: {r[2]},\tNombre: {r[1]}")
    except:
        messagebox.showerror(message=f"La tabla STOCK no existe")

    try:
        print(f"\n---------- PEDIDO ----------\n")
        for r in cursor.execute(f"select * from PEDIDO"):
            print(f"Pedido: {r[0]},\tCliente: {r[1]},\tFecha: {r[2].date()}")
    except:
        messagebox.showerror(message=f"La tabla PEDIDO no existe")

def crearStock():
    global cursor

    # Comprobamos que las tablas existen, en dicho caso se destruyen
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
    
    # Verificar si se ha introducido un código de producto y una cantidad de producto
    try:
    	prueba1 = int(producto.get())
    	prueba2 = int(cantidad.get())
    except ValueError:
    	messagebox.showinfo(title="Entrada", message="Se debe introducir un código de producto y una cantidad de producto")
    else:
    	# Verificar si el código de producto existe
    	cursor.execute(f"select count(cProducto) from STOCK where cProducto='{int(producto.get())}'")
    	if cursor.fetchone()[0] == 0:
        	messagebox.showinfo(title="Producto", message="Código de producto no existente")

    	# Verificar si el producto ya ha sido introducido previamente
    	cursor.execute(f"select count(*) from DetallePedido where cProducto = '{int(producto.get())}' and cPedido = '{contador_pedidos}'")
    	if cursor.fetchone()[0] > 0:
        	messagebox.showinfo(title="Producto", message="Ya has añadido ese producto al Pedido")
    	else:        	
        	# Verificar que hay cantidad suficiente del producto
        	cursor.execute(f"select Cantidad from STOCK where cProducto = '{int(producto.get())}'")
        	if int(cursor.fetchone()[0]) >= int(cantidad.get()):
        		cursor.execute(f"insert into DETALLEPEDIDO values({contador_pedidos}, {int(producto.get())}, {int(cantidad.get())})")
        		cursor.execute(f"update STOCK set Cantidad = Cantidad - {int(cantidad.get())} where cProducto = {int(producto.get())}")
        		# Mostramos el contenido de la base de datos
        		mostrarContenidoTablas()
        	else:
            		messagebox.showinfo(title="Producto", message="Cantidad de producto insuficiente")

def detallePedido():
    global subwindow, contador_pedidos

    detallePedidoWindow = tk.Toplevel()
    detallePedidoWindow.title("Detalle Pedido")
    detallePedidoWindow.geometry("500x500")
    detallePedidoWindow.configure(background="#E1FBFF")

    # Recogemos la información del pedido
    producto = tk.StringVar(detallePedidoWindow)
    tk.Label(detallePedidoWindow, text="Código Producto", bg="#E1FBFF", fg="#27ADC1", justify="center").pack(pady=10)
    tk.Entry(detallePedidoWindow, justify="center", textvariable=producto).pack(pady=10)

    cantidad = tk.StringVar(detallePedidoWindow)
    tk.Label(detallePedidoWindow, text="Cantidad", bg="#E1FBFF", fg="#27ADC1", justify="center").pack(pady=10)
    tk.Entry(detallePedidoWindow, justify="center", textvariable=cantidad).pack(pady=10)
    tk.Button(detallePedidoWindow, text="Añadir Datos", bg="#27ADC1", fg="#E1FBFF", width=20, command=lambda:recogerDatos(producto, cantidad)).pack()
    tk.Button(detallePedidoWindow, text="Cerrar", bg="#27ADC1", fg="#E1FBFF", width=20, command=detallePedidoWindow.destroy).pack()

def eliminarDetallePedido():
    global cursor

    cursor.execute("rollback to DetallePedido")

    # Mostramos el contenido de la base de datos
    mostrarContenidoTablas()

def crearPedido(cliente):
    global cursor, clientwindow, contador_pedidos

    # Savepoint previo a crear pedido
    cursor.execute(f"savepoint Pedido")
    
    # Actualizamos contador_pedidos con el número de tuplas en la tabla PEDIDO
    cursor.execute(f"select count(*) from PEDIDO")
    contador_pedidos = cursor.fetchone()[0]
    
    # Verificar si se ha introducido un código de cliente
    try:
    	# Insertamos el pedido en su correspondiente tabla
    	cursor.execute(f"insert into PEDIDO values ({contador_pedidos}, {int(cliente.get())}, CURRENT_DATE)")
    except ValueError:
    	messagebox.showinfo(title="Entrada", message="Se debe introducir un código de cliente")
    	
    # Savepoint previo a crear cualquiera de los detallepedido
    cursor.execute(f"savepoint DetallePedido")

    # Destruimos la subventana
    clientwindow.destroy()
    
def cancelarPedido():
    global cursor, subwindow, window

    cursor.execute("rollback to Pedido")

    # Mostramos el contenido de la base de datos
    mostrarContenidoTablas()

    # Destruimos la subventana
    subwindow.destroy()

    # Remostramos la ventana
    window.deiconify()

def finalizarPedido():
    global cursor, subwindow, window, contador_pedidos

    cursor.execute("commit")

    # Incrementamos el contador de pedidos
    contador_pedidos = contador_pedidos + 1

    # Destruimos la subventana
    subwindow.destroy()

    # Remostramos la ventana
    window.deiconify()

def altaPedido():
    global cursor, window, subwindow, clientwindow, contador_pedidos

    # Creamos la ventana para introducir los datos del cliente
    clientwindow = tk.Toplevel()
    clientwindow.title("Datos Cliente")
    clientwindow.geometry("500x500")
    clientwindow.configure(background="#E1FBFF", pady=20)
    clientwindow.focus()

    # Creamos la ventana del submenú
    subwindow = tk.Toplevel()
    subwindow.title("Dar de Alta Pedido")
    subwindow.geometry("700x700")
    subwindow.configure(background="#E1FBFF", pady=20)

    # Encabezado de la ventana
    tk.Label(subwindow, text="Dar de Alta Pedido", bg="#E1FBFF", fg="#27ADC1", font=("Arial", 16)).pack()

    # Introducir código de cliente
    cliente = tk.StringVar(clientwindow)
    tk.Label(clientwindow, text="Código Cliente", bg="#E1FBFF", fg="#27ADC1", justify="center").pack()
    tk.Entry(clientwindow, justify="center", textvariable=cliente).pack(pady=10)
    tk.Button(clientwindow, text="Añadir cliente", bg="#27ADC1", fg="#E1FBFF", width=20, state="normal", command=lambda:crearPedido(cliente)).pack(pady=10)

    # Botones del menú
    #tk.Button(clienteWindow, text="Cerrar", bg="#27ADC1", fg="#E1FBFF", width=10, command=clienteWindow.destroy).pack()
    tk.Button(subwindow, text="Añadir detalle de producto", bg="#27ADC1", fg="#E1FBFF", width=35, height=3, command=detallePedido).pack()
    tk.Button(subwindow, text="Eliminar todos los detalles de producto", bg="#27ADC1", fg="#E1FBFF", width=35, height=3, command=eliminarDetallePedido).pack()
    tk.Button(subwindow, text="Cancelar Pedido", bg="#27ADC1", fg="#E1FBFF", width=35, height=3, command=cancelarPedido).pack()
    tk.Button(subwindow, text="Finalizar Pedido", bg="#27ADC1", fg="#E1FBFF", width=35, height=3, command=finalizarPedido).pack()

    # Ocultamos la ventana
    window.withdraw()

def salir():
    global window

    # Cerramos la conexión
    db_close()

    # Destruimos la ventana
    window.destroy()

def main():
    global window

    # Conexión a la base de datos
    db_connect()

    # Configuración de la ventana principal
    window = tk.Tk()
    window.title("Menú Principal")
    window.geometry("700x700")
    window.configure(background="#E1FBFF", pady=20)

    # Encabezado de la ventana
    tk.Label(window, text="Menú Principal", bg="#E1FBFF", fg="#27ADC1", font=("Arial", 16)).pack()

    # Imagen
    imagen = tk.PhotoImage(file="resources/carro.png")
    tk.Label(window, bg="#E1FBFF", image=imagen).pack()

    # Botones del menú
    tk.Button(window, text="Crear Stock", bg="#27ADC1", fg="#E1FBFF", width=35, height=3, command=crearStock).pack()
    tk.Button(window, text="Dar de Alta Pedido", bg="#27ADC1", fg="#E1FBFF", width=35, height=3, command=altaPedido).pack()
    tk.Button(window, text="Mostrar Contenido Tablas", bg="#27ADC1", fg="#E1FBFF", width=35, height=3, command=mostrarContenidoTablas).pack()
    tk.Button(window, text="Salir", bg="#27ADC1", fg="#E1FBFF", width=35, height=3,command=salir).pack()

    # Ejecutar la ventana
    window.mainloop()

if __name__ == "__main__":
    main()
