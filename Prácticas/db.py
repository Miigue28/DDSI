import oracledb
import db_config
import tkinter as tk
import csv
from tkinter import messagebox
from datetime import date

# Global Variables
cursor = None
connection = None

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

def createTables():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PuestoSueldo (
        Puesto VARCHAR(20) CONSTRAINT puesto_clave_primaria PRIMARY KEY,
        Sueldo NUMBER
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Empleado (
            cEmpleado VARCHAR(10) CONSTRAINT codigo_empleado_clave_primaria PRIMARY KEY,
            Nombre VARCHAR(20),
            Apellidos VARCHAR(40),
            DNI VARCHAR(9) UNIQUE,
            CorreoElectronico VARCHAR(30)
            Puesto CONSTRAINT puesto_clave_externa REFERENCES PuestoSueldo(Puesto)
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cliente (
            DNI VARCHAR(9) CONSTRAINT dni_cliente_clave_primaria PRIMARY KEY,
            Nombre VARCHAR(20),
            Apellidos VARCHAR(40),
            CorreoElectronico VARCHAR(30)
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reservas (
            cReserva VARCHAR(10) CONSTRAINT codigo_reserva_clave_primaria PRIMARY KEY,
            Precio NUMBER,
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TieneReserva (
            cReserva CONSTRAINT codigo_reserva_clave_externa REFERENCES Reservas(cReserva) PRIMARY KEY,
            DNI CONSTRAINT dni_clave_externa REFERENCES Cliente(DNI)
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Servicios (
            cServicio VARCHAR(10) CONSTRAINT codigo_servicio_clave_primaria PRIMARY KEY,
            Precio NUMBER,
            PlazasTotales INTEGER,
            PlazasLibres INTEGER
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Asociado (
            cReserva CONSTRAINT codigo_reserva_clave_externa REFERENCES Reservas(cReserva),
            Descripcion VARCHAR(500)
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS NombreDescripcion (
            Nombre CONSTRAINT nombre_clave_primaria PRIMARY KEY,
            Descripcion VARCHAR(500)
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ActividadesTuristicas (
            cServicio CONSTRAINT codigo_servicio_clave_externa REFRENCES Servicios(cServicio) PRIMARY KEY,
            Nombre CONSTRAINT nombre_clave_externa REFERENCES NombreDescripcion(Nombre),
            Tipo VARCHAR(20),
            FechaInicio DATE,
            FechaFin DATE,
            HoraInicio TIME,
            HoraFin TIME,
            Ubicacion VARCHAR(30),
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transportes (
            cServicio CONSTRAINT codigo_actividad_turistica_clave_externa REFRENCES Servicios(cServicio) PRIMARY KEY,
            Tipo VARCHAR(30),
            Fecha DATE,
            Hora TIME,
            Compañia VARCHAR(30),
            Origen VARCHAR(30),
            Destino VARCHAR(30)
    )""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Alojamientos (
            cServicio CONSTRAINT codigo_servicio_clave_externa REFRENCES Servicios(cServicio) PRIMARY KEY,
            Nombre VARCHAR(50),
            Tipo VARCHAR(20),
            FechaEntrada DATE,
            FechaSalida DATE,
            Ubicacion VARCHAR(30),
            Telefono VARCHAR(9)
    )""")
        

def mostrarContenidoTablas(nombreTabla):
    global cursor
    
    try:
        print(f"\n---------- {nombreTabla} ----------\n")
        cursor.execute(f"select * from {nombreTabla}")
        columns = [col[0] for col in cursor.description]
        
        print("\t".join(columns))  # Imprimir nombres de columnas
        print("-" * 50)
            
        for row in cursor:
            print("\t".join(map(str, row)))
            
    except:
        messagebox.showerror(message=f"La tabla 'nombreTabla' no existe")
    