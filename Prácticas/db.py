import oracledb
import db_config
import click
import csv
from flask import g

# Global Variables
connection = None

def get_db():
    if 'db' not in g:
        cp = oracledb.ConnectParams(user=db_config.user, password=db_config.password, host="oracle0.ugr.es", port=1521, service_name="practbd")
        g.db = oracledb.connect(params=cp)

        click.echo('Conexión extablecida')

    return g.db.cursor()


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():

    cursor = get_db()

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
            Nombre VARCHAR(50),
            Tipo VARCHAR(20),
            FechaHoraInicio DATE,
            FechaHoraFin DATE,
            Ubicacion VARCHAR(30)
    )""")

    cursor.execute("""
        CREATE TABLE Transportes (
            cServicio REFERENCES Servicios(cServicio) PRIMARY KEY,
            Tipo VARCHAR(30),
            FechaHora DATE,
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
        CREATE OR REPLACE TRIGGER sueldoNegativo
            BEFORE INSERT ON PuestoSueldo
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
                raise_application_error(-20600, :new.Precio || ' El precio no puede ser negativo');
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
                UPDATE Reservas SET Precio = Precio + (SELECT Precio FROM Servicios WHERE cServicio = :new.cServicio)
                   WHERE cReserva=:new.cReserva;
            ELSE
                UPDATE Reservas SET Precio = Precio - (SELECT Precio FROM Servicios WHERE cServicio = :old.cServicio)
                WHERE cReserva=:old.cReserva;
            END IF;
        END;
    """)

    #Disparador para impedir que se inserte una fecha de fin anterior a la fecha de inicio de una actividad turística
    cursor.execute("""
        CREATE OR REPLACE TRIGGER fechasHorasCorrectasActividades
            BEFORE INSERT OR UPDATE ON ActividadesTuristicas
            FOR EACH ROW
        BEGIN
            IF :new.FechaHoraInicio > :new.FechaHoraFin THEN
                raise_application_error(-20600, :new.FechaHoraInicio || :new.FechaHoraFin || ' La fecha y hora de inicio debe ser anterior a la fecha y hora de fin');
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
            cursor.execute("commit")

    with open("empleados.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Empleados values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}')")
            cursor.execute("commit")

    with open("clientes.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Clientes values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}')")
            cursor.execute("commit")

    with open("Reservas.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Reservas values('{row[0]}', '{row[1]}')")
            cursor.execute("commit")

    with open("TieneReserva.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into TieneReserva values('{row[0]}', '{row[1]}')")
            cursor.execute("commit")

    with open("servicios.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Servicios values('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}')")
            cursor.execute("commit")

    with open("Asociado.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Asociado values('{row[0]}', '{row[1]}')")
            cursor.execute("commit")

    with open("ActividadesTuristicas.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into ActividadesTuristicas values('{row[0]}', '{row[1]}', '{row[2]}', TO_DATE('{row[3]}', 'DD/MM/RR HH24:MI'), TO_DATE('{row[4]}', 'DD/MM/RR HH24:MI'), '{row[5]}')")
            cursor.execute("commit")

    with open("Transportes.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Transportes values('{row[0]}', '{row[1]}', TO_DATE('{row[2]}', 'DD/MM/RR HH24:MI'), '{row[3]}', '{row[4]}', '{row[5]}')")
            cursor.execute("commit")

    with open("Alojamientos.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute(f"insert into Alojamientos values('{row[0]}', '{row[1]}', '{row[2]}', TO_DATE('{row[3]}', 'DD/MM/RR'), TO_DATE('{row[4]}', 'DD/MM/RR'), '{row[5]}', '{row[6]}')")
            cursor.execute("commit")


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


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
    
