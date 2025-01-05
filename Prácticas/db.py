import oracledb
import db_config
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

    # Borramos las tablas existentes
    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'EMPLEADOS'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table Empleados")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'PUESTOSUELDO'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table PuestoSueldo")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'TIENERESERVA'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table TieneReserva")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'ASOCIADO'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table Asociado")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'ACTIVIDADESTURISTICAS'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table ActividadesTuristicas")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'TRANSPORTES'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table Transportes")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'ALOJAMIENTOS'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table Alojamientos")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'NOMBREDESCRIPCION'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table NombreDescripcion")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'SERVICIOS'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table Servicios")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'RESERVAS'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table Reservas")

    cursor.execute(f"select count(*) from user_tables where upper(table_name) = 'CLIENTES'")
    if cursor.fetchone()[0] > 0:
        cursor.execute("drop table Clientes")


    #Creamos las tablas
    cursor.execute("""
    CREATE TABLE PuestoSueldo (
        Puesto VARCHAR(20) PRIMARY KEY,
        Sueldo FLOAT
    )""")

    cursor.execute("""
        CREATE TABLE Empleados (
            cEmpleado VARCHAR(10) PRIMARY KEY,
            Nombre VARCHAR(20),
            Apellidos VARCHAR(40),
            DNI VARCHAR(9) UNIQUE,
            CorreoElectronico VARCHAR(30),
            Puesto REFERENCES PuestoSueldo(Puesto)
    )""")

    cursor.execute("""
        CREATE TABLE Clientes (
            DNI VARCHAR(9) PRIMARY KEY,
            Nombre VARCHAR(20),
            Apellidos VARCHAR(40),
            CorreoElectronico VARCHAR(30)
    )""")

    cursor.execute("""
        CREATE TABLE Reservas (
            cReserva VARCHAR(10) PRIMARY KEY,
            Precio FLOAT DEFAULT 0
    )""")

    cursor.execute("""
        CREATE TABLE TieneReserva (
            cReserva REFERENCES Reservas(cReserva) PRIMARY KEY,
            DNI REFERENCES Clientes(DNI) ON DELETE CASCADE
    )""")

    cursor.execute("""
        CREATE TABLE Servicios (
            cServicio VARCHAR(10) PRIMARY KEY,
            Precio FLOAT,
            PlazasTotales INTEGER,
            PlazasLibres INTEGER
    )""")

    cursor.execute("""
        CREATE TABLE Asociado (
            cReserva REFERENCES Reservas(cReserva) ON DELETE CASCADE,
            cServicio REFERENCES Servicios(cServicio) ON DELETE CASCADE,
            PRIMARY KEY (cReserva, cServicio)
    )""")

    cursor.execute("""
        CREATE TABLE NombreDescripcion (
            Nombre VARCHAR(50) PRIMARY KEY,
            Descripcion VARCHAR(500)
    )""")

    cursor.execute("""
        CREATE TABLE ActividadesTuristicas (
            cServicio REFERENCES Servicios(cServicio) PRIMARY KEY,
            Nombre REFERENCES NombreDescripcion(Nombre),
            Tipo VARCHAR(20),
            FechaInicio DATE,
            FechaFin DATE,
            HoraInicio TIMESTAMP,
            HoraFin TIMESTAMP,
            Ubicacion VARCHAR(30)
    )""")

    cursor.execute("""
        CREATE TABLE Transportes (
            cServicio REFERENCES Servicios(cServicio) PRIMARY KEY,
            Tipo VARCHAR(30),
            Fecha DATE,
            Hora TIMESTAMP,
            Compañia VARCHAR(30),
            Origen VARCHAR(30),
            Destino VARCHAR(30)
    )""")

    cursor.execute("""
        CREATE TABLE Alojamientos (
            cServicio REFERENCES Servicios(cServicio) PRIMARY KEY,
            Nombre VARCHAR(50),
            Tipo VARCHAR(20),
            FechaEntrada DATE,
            FechaSalida DATE,
            Ubicacion VARCHAR(30),
            Telefono VARCHAR(9)
    )""")

    #Disparadores
    
    #Disparador para impedir que se inserte un sueldo negativo
    cursor.execute("""
        CREATE OR REPLACE TRIGGER sueldoNoNegativo
            BEFORE INSERT OR UPDATE ON PuestoSueldo
            FOR EACH ROW
        BEGIN
            IF :new.Sueldo < 0 THEN
                raise_application_error(-20600, :new.Sueldo || ' El sueldo no puede ser negativo');
            END IF;
        END;
    """)

    #Disparador para impedir que se inserte un precio de servicio negativo
    cursor.execute("""
        CREATE OR REPLACE TRIGGER precioNoNegativo
            BEFORE INSERT OR UPDATE ON Servicios
            FOR EACH ROW
        BEGIN
            IF :new.Precio < 0 THEN
                raise_application_error(-20600, :new.Precio || ' El sueldo no puede ser negativo');
            END IF;
        END;
    """)

    #Disparador para que al asociar (o eliminar) un servicio a una reserva, sume (o reste) el precio del servicio al precio de la reserva.
    cursor.execute("""
        CREATE OR REPLACE TRIGGER nuevoPrecio
            AFTER INSERT OR DELETE ON Asociado
            FOR EACH ROW
        BEGIN
            IF INSERTING THEN
                UPDATE Reservas SET Precio = Precio + (SELECT Precio FROM Servicios WHERE cServicio = :new.cServicio);
            ELSE
                UPDATE Reservas SET Precio = Precio - (SELECT Precio FROM Servicios WHERE cServicio = :old.cServicio);
            END IF;
        END;
    """)

    #Disparador para impedir que se inserte una fecha de fin anterior a la fecha de inicio de una actividad turística
    cursor.execute("""
        CREATE OR REPLACE TRIGGER fechasCorrectasActividades
            BEFORE INSERT OR UPDATE ON ActividadesTuristicas
            FOR EACH ROW
        BEGIN
            IF :new.FechaInicio > :new.FechaFin THEN
                raise_application_error(-20600, :new.FechaInicio || :new.FechaFin || ' La fecha de inicio debe ser anterior a la fecha de fin');
            END IF;
        END;
    """)

    #Disparador para impedir que se inserte una hora de fin anterior a la hora de inicio de una actividad turística
    cursor.execute("""
        CREATE OR REPLACE TRIGGER horasCorrectasActividades
            BEFORE INSERT OR UPDATE ON ActividadesTuristicas
            FOR EACH ROW
        BEGIN
            IF :new.HoraInicio >= :new.HoraFin THEN
                raise_application_error(-20600, :new.HoraInicio || :new.HoraFin || ' La hora de inicio debe ser anterior a la hora de fin');
            END IF;
        END;
    """)

    #Disparador para impedir que se inserte una fecha de salida anterior a la fecha de entrada de un alojamiento
    cursor.execute("""
        CREATE OR REPLACE TRIGGER fechasCorrectasAlojamientos
            BEFORE INSERT OR UPDATE ON Alojamientos
            FOR EACH ROW
        BEGIN
            IF :new.FechaEntrada > :new.FechaSalida THEN
                raise_application_error(-20600, :new.FechaEntrada || :new.FechaSalida || ' La fecha de entrada debe ser anterior a la fecha de salida');
            END IF;
        END;
    """)

    #Disparador para impedir que se inserte un numero de plazas libres mayor al numero de plazas totales de un servicio
    cursor.execute("""
        CREATE OR REPLACE TRIGGER plazasCorrectas
            BEFORE INSERT OR UPDATE ON Servicios
            FOR EACH ROW
        BEGIN
            IF :new.PlazasLibres > :new.PlazasTotales THEN
                raise_application_error(-20600, :new.PlazasLibres || :new.PlazasTotales || ' El sueldo no puede ser negativo');
            END IF;
        END;
    """)

    #Insertamos tuplas
    with open("PuestoSueldo.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into PuestoSueldo values('{row[0]}', '{row[1]}')")

    with open("empleados.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Empleados values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}')")

    with open("clientes.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Clientes values('{row[0]}', '{row[1]}','{row[2]}', '{row[3]}')")

    with open("Reservas.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Reservas values('{row[0]}', '{row[1]}')")

    with open("TieneReserva.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into TieneReserva values('{row[0]}', '{row[1]}')")

    with open("servicios.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Servicios values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}')")

    with open("Asociado.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Asociado values('{row[0]}', '{row[1]}')")

    with open("NombreDescripcion.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into NombreDescripcion values('{row[0]}', '{row[1]}')")

    with open("ActividadesTuristicas.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into ActividadesTuristicas values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}', '{row[6]}', '{row[7]}')")

    with open("Transportes.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Transportes values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}', '{row[6]}')")

    with open("Alojamientos.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Alojamientos values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}', '{row[6]}')")


        

#def mostrarContenidoTablas(nombreTabla):
#    global cursor
#    
#    try:
#        print(f"\n---------- {nombreTabla} ----------\n")
#        cursor.execute(f"select * from {nombreTabla}")
#        columns = [col[0] for col in cursor.description]
#        
#        print("\t".join(columns))  # Imprimir nombres de columnas
#        print("-" * 50)
#            
#        for row in cursor:
#            print("\t".join(map(str, row)))
#            
#    except:
#        messagebox.showerror(message=f"La tabla 'nombreTabla' no existe")
    
