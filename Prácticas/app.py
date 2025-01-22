from flask import Flask, render_template, request, flash, redirect, url_for
from db import get_db, init_db

# Create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'GRXViajes'

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/clients')
def clients():
    db = get_db()

    clients = db.execute("""
        SELECT * FROM Clientes
    """).fetchall()

    return render_template('clients.html', clients=clients)

@app.route('/clients/insert', methods=['POST'])
def insert_client():
    db = get_db()
    error = None

    dni = request.form['dni']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']

    if db.execute(f"""
        SELECT count(*) FROM Clientes where DNI='{dni}'
    """).fetchone()[0] > 0:
        error = 'Cliente ya existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"""
            INSERT INTO Clientes VALUES('{dni}', '{name}', '{surname}', '{email}')
        """)
        db.execute("COMMIT")
    
    return redirect(url_for('clients'))

@app.route('/clients/delete', methods=['POST'])
def delete_client():
    db = get_db()
    error = None

    dni = request.form['dni']

    if db.execute(f"""
        SELECT count(*) FROM Clientes where DNI='{dni}'
    """).fetchone()[0] == 0:
        error = 'Cliente no existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"DELETE FROM Clientes WHERE DNI='{dni}'")
        db.execute("COMMIT")
    
    return redirect(url_for('clients'))

@app.route('/clients/update', methods=['POST'])
def update_client():
    db = get_db()
    error = None
    
    dni = request.form['dni']
    nombre = request.form['name']
    apellidos = request.form['surname']
    email = request.form['email']

    if db.execute(f"""
        SELECT count(*) FROM Clientes where DNI='{dni}'
    """).fetchone()[0] == 0:
        error = 'Cliente no existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"""
            UPDATE Clientes SET Nombre='{nombre}', Apellidos='{apellidos}', CorreoElectronico='{email}' WHERE DNI='{dni}'
        """)
        db.execute("COMMIT")

    return redirect(url_for('clients'))

@app.route('/clients/ask')
def ask_client():
    return render_template('ask_client.html')

@app.route('/employees')
def employees():
    db = get_db()

    employees = db.execute("""
        SELECT * FROM Empleados NATURAL JOIN (SELECT * FROM PuestoSueldo)
    """).fetchall()

    return render_template('employees.html', employees=employees)

@app.route('/employees/insert', methods=['POST'])
def insert_employee():
    db = get_db()
    error = None

    codigo = request.form['code']
    dni = request.form['dni']
    nombre = request.form['name']
    apellidos = request.form['surnames']
    correo = request.form['email']
    puesto = request.form['position']

    if db.execute(f"""
        SELECT count(*) FROM Empleados where DNI='{dni}'
    """).fetchone()[0] > 0:
        error = 'Empleado ya existente'

    if db.execute(f"""
        SELECT count(*) FROM PuestoSueldo where Puesto='{puesto}'
    """).fetchone()[0] == 0:
        error = 'Puesto no existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"""
            INSERT INTO Empleados 
            VALUES('{codigo}', '{nombre}', '{apellidos}', '{dni}', '{correo}', '{puesto}')
        """)
        db.execute("COMMIT")

    return redirect(url_for('employees'))

@app.route('/employees/delete', methods=['POST'])
def delete_employee():
    db = get_db()
    error = None

    codigo = request.form['code']

    if db.execute(f"""
        SELECT count(*) FROM Empleados where cEmpleado='{codigo}'
    """).fetchone()[0] == 0:
        error = 'Código de empleado no existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"DELETE FROM Empleados WHERE cEmpleado='{codigo}'")
        db.execute("COMMIT")
    
    return redirect(url_for('employees'))


@app.route('/employees/update', methods=['POST'])
def update_employee():
    db = get_db()
    error = None
    
    codigo = request.form['code']
    dni = request.form['dni']
    nombre = request.form['name']
    apellidos = request.form['surnames']
    correo = request.form['email']
    puesto = request.form['position']

    if db.execute(f"""
        SELECT count(*) FROM Empleados where DNI='{dni}'
    """).fetchone()[0] == 0:
        error = 'Empleado no existente'

    if db.execute(f"""
        SELECT count(*) FROM PuestoSueldo where Puesto='{puesto}'
    """).fetchone()[0] == 0:
        error = 'Puesto no existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"""
            UPDATE Empleados SET Nombre='{nombre}', Apellidos='{apellidos}', DNI='{dni}', CorreoElectronico='{correo}', Puesto='{puesto}' WHERE cEmpleado='{codigo}'
        """)
        db.execute("COMMIT")

    return redirect(url_for('employees'))

@app.route('/employees/ask')
def ask_employee():
    return render_template('ask_employee.html')

@app.route('/activities')
def activities():
    return render_template('activities.html')

@app.route('/insert_activities', methods=['GET', 'POST'])
def insert_activities():
    db = get_db()
    if request.method == 'POST':
        codigo = request.form['code']
        nombre = request.form['name']
        tipo = request.form['type']
        ubicacion = request.form['location']
        fechaInicio = request.form['start date']
        fechaInicio = fechaInicio.replace("T", " ")
        fechaFin = request.form['end date']
        fechaFin = fechaFin.replace("T", " ")
        plazasTotales= request.form['total_seats']
        plazasLibres = request.form['available_seats']
        precio = request.form['price']
        error = None

        if db.execute(f"""
            SELECT count(*) FROM Servicios where cServicio='{codigo}'
        """).fetchone()[0] > 0:
            error = 'Código de actividad ya existente'

        if error is not None:
            flash(error)
        else:
            db.execute(f"insert into Servicios values('{codigo}', '{precio}', '{plazasTotales}', '{plazasLibres}')")
            db.execute(
                f"insert into ActividadesTuristicas values('{codigo}', '{nombre}', '{tipo}', TO_DATE('{fechaInicio}', 'YYYY-MM-DD HH24:MI'), TO_DATE('{fechaFin}', 'YYYY-MM-DD HH24:MI'), '{ubicacion}')"
            )
            db.execute("commit")
    
    activities = db.execute(
        """SELECT * FROM ActividadesTuristicas NATURAL JOIN (SELECT * FROM Servicios)"""
    ).fetchall()

    return render_template('insert_activities.html',activities=activities)

@app.route('/<int:id>/delete', methods=('POST',))
def delete_activities():    
    return redirect(url_for(''))

@app.route('/activities/update', methods=('GET', 'POST'))
def update_activities():
    return render_template('blog/update.html')

@app.route('/transports')
def transports():
    db = get_db()

    transports = db.execute("""
        SELECT * FROM Transportes NATURAL JOIN (SELECT * FROM Servicios)
    """).fetchall()

    return render_template('transports.html',transports=transports)

@app.route('/transports/insert', methods=['POST'])
def insert_transport():
    db = get_db()
    error = None

    codigo = request.form['code']
    compania = request.form['company']
    tipo = request.form['type']
    fecha = request.form['date']
    fecha = fecha.replace("T", " ")
    origen = request.form['origin']
    destino = request.form['destination']
    plazasTotales= request.form['total_seats']
    plazasLibres = request.form['available_seats']
    precio = request.form['price']

    if db.execute(f"""
        SELECT count(*) FROM Servicios where cServicio='{codigo}'
    """).fetchone()[0] > 0:
        error = 'Código de transporte ya existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"""
            INSERT INTO Servicios VALUES('{codigo}', '{precio}', '{plazasTotales}', '{plazasLibres}')
        """)
        db.execute(f"""
            INSERT INT Transportes VALUES('{codigo}', '{tipo}', TO_DATE('{fecha}', 'YYYY-MM-DD HH24:MI'), '{compania}', '{origen}', '{destino}')
        """)
        db.execute("COMMIT")
    
    return redirect(url_for('transports'))

@app.route('/transports/delete', methods=['POST'])
def delete_transport():  
    db = get_db()
    error = None

    codigo = request.form['code']

    if db.execute(f"""
        SELECT count(*) FROM Servicios where cServicio='{codigo}'
    """).fetchone()[0] == 0:
        error = 'Código de transporte no existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"DELETE FROM Transportes WHERE cServicio='{codigo}'")
        db.execute(f"DELETE FROM Servicios WHERE cServicio='{codigo}'")
        db.execute("COMMIT")
    
    return redirect(url_for('transports'))

@app.route('/transports/update', methods=['POST'])
def update_transport():
    db = get_db()
    error = None

    codigo = request.form['code']
    compania = request.form['company']
    tipo = request.form['type']
    fecha = request.form['date']
    fecha = fecha.replace("T", " ")
    origen = request.form['origin']
    destino = request.form['destination']
    plazasTotales= request.form['total_seats']
    precio = request.form['price']

    if db.execute(f"""
        SELECT count(*) FROM Servicios where cServicio='{codigo}'
    """).fetchone()[0] == 0:
        error = 'Código de transporte no existente'

    if error is not None:
        flash(error)
    else:
        db.execute(f"""
            UPDATE Servicios SET Precio='{precio}', PlazasTotales='{plazasTotales}' WHERE cServicio='{codigo}'
        """)
        db.execute(f"""
            UPDATE Transportes SET Tipo='{tipo}', FechaHora=TO_DATE('{fecha}', 'YYYY-MM-DD HH24:MI'), Compañia='{compania}', Origen='{origen}', Destino='{destino}' WHERE cServicio='{codigo}'
        """)
        db.execute("COMMIT")
    
    return redirect(url_for('transports'))

@app.route('/accomodations')
def accomodations():
    return render_template('accomodations.html')

@app.route('/insert_accomodations', methods=['GET', 'POST'])
def insert_accomodations():
    db = get_db()
    if request.method == 'POST':
        codigo = request.form['code']
        nombre = request.form['name']
        tipo = request.form['type']
        ubicacion = request.form['location']
        fechaEntrada = request.form['entry date']
        fechaSalida = request.form['departure date']
        telefono = request.form['phone number']
        plazasTotales= request.form['total_seats']
        plazasLibres = request.form['available_seats']
        precio = request.form['price']
        error = None

        if db.execute(f"""
            SELECT count(*) FROM Servicios where cServicio='{codigo}'
        """).fetchone()[0] > 0:
            error = 'Código de alojamiento ya existente'

        if error is not None:
            flash(error)
        else:
            db.execute(f"insert into Servicios values('{codigo}', '{precio}', '{plazasTotales}', '{plazasLibres}')")
            db.execute(
                f"insert into Alojamientos values('{codigo}', '{nombre}', '{tipo}', TO_DATE('{fechaEntrada}', 'YYYY-MM-DD'), TO_DATE('{fechaSalida}', 'YYYY-MM-DD'), '{ubicacion}', '{telefono}')"
            )
            db.execute("commit")
    
    accomodations = db.execute(
        """SELECT * FROM Alojamientos NATURAL JOIN (SELECT * FROM Servicios)"""
    ).fetchall()

    return render_template('insert_accomodations.html',accomodations=accomodations)

@app.route('/accomodations/<int:id>/delete', methods=('POST',))
def delete_accomodations():
    
    codigo = request.form['code']
    error = None

    if db.execute(f"""
            SELECT count(*) FROM Alojamientos where cServicio='{codigo}'
        """).fetchone()[0] == 0:
            error = 'Código de alojamiento no existente'

    if error is not None:
        flash(error)
    
    else:
        db = get_db()
        db.execute(f"DELETE FROM Alojamientos WHERE cServicio = '{codigo}' ")
        db.commit()
    
    return render_template('delete')

@app.route('/accomodations/update', methods=('GET', 'POST'))
def update_accomodations():
    
    if request.method == 'POST':
        codigo = request.form['code']
        fechaEntrada = request.form['entry date']
        fechaSalida = request.form['departure date']
        telefono = request.form['phone number']
        plazasTotales= request.form['total_seats']
        plazasLibres = request.form['available_seats']
        precio = request.form['price']
        error = None

        if db.execute(f"""
            SELECT count(*) FROM Alojamientos where cServicio='{codigo}'
        """).fetchone()[0] == 0:
            error = 'Código de alojamiento no existente'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            
            db.execute(f"UPDATE Alojamientos SET FechaEntrada = TO_DATE('{fechaEntrada}', 'YYYY-MM-DD'), FechaSalida = TO_DATE('{fechaSalida}', 'YYYY-MM-DD'), Telefono = '{telefono}' WHERE cServicio = '{codigo}'")

            db.execute(f"UPDATE Servicios SET PlazasTotales = '{plazasTotales}', PlazasLibres = '{plazasLibres}', Precio = '{precio}' WHERE cServicio = '{codigo}'")
            
            
            db.commit()
            return redirect(url_for(''))

    return render_template('blog/update.html')

@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    db = get_db()
    reservation = ''
    dni = ''
    service = ''

    if request.method == 'POST':
        reservation = request.form['reservation']
        dni = request.form['dni']
        service = request.form['service']
        error = None

        if db.execute(f"""
            SELECT count(*) FROM Servicios where cServicio='{service}'
        """).fetchone()[0] == 0:
            error = 'Código de servicio no existente'

        if db.execute(f"""
            SELECT count(*) FROM Clientes where DNI='{dni}'
        """).fetchone()[0] == 0:
            error = 'Cliente no existente'

        if error is not None:
            flash(error)
        else:
            # TODO: Comprobar que hay plazas disponibles del servicio
            # TODO: En dicho caso restarle una plaza
            price = db.execute(f"""
                SELECT Precio FROM Servicios WHERE cServicio='{service}'
            """).fetchone()[0]

            # Insertamos la reserva
            db.execute(f"""
                INSERT INTO Reservas VALUES ('{reservation}', '{price}')       
            """)
            db.execute(f"""
                INSERT INTO TieneReserva VALUES ('{reservation}', '{dni}')           
            """)
            db.execute(f"""
                INSERT INTO Asociado VALUES ('{reservation}', '{service}')           
            """)
            db.execute("commit");
    else:
        # Capturar parámetros de consulta
        reservation = request.args.get('reservation', default='', type=str)
        dni = request.args.get('dni', default='', type=str)
        service = request.args.get('service', default='', type=str)

    bookings = db.execute("""
    SELECT * FROM Reservas NATURAL JOIN (SELECT * FROM TieneReserva) NATURAL JOIN (SELECT * FROM Asociado)
    """).fetchall()
    return render_template('table_bookings.html', bookings=bookings, reservation=reservation, dni=dni, service=service)

@app.route('/bookings/delete', methods=['POST'])
def delete_reservation():
    db = get_db()
    reservation = request.form['reservation']
    dni = request.form['dni']
    service = request.form['service']
    error = None

    if db.execute(f"""
        SELECT count(*) FROM Reservas where cReserva='{reservation}'
    """).fetchone()[0] == 0:
        error = 'Código de reserva no existente'

    # Si el campo del código de servicio está relleno significa que queremos eliminarlo de la reserva
    if service != "":
        if db.execute(f"""
            SELECT count(*) FROM Servicios where cServicio='{service}'
        """).fetchone()[0] == 0:
            error = 'Código de servicio no existente'

        if db.execute(f"""
            SELECT count(*) FROM Clientes where DNI='{dni}'
        """).fetchone()[0] == 0:
            error = 'Cliente no existente'

    if error is not None:
        flash(error)
    else:
        if service != "":
            db.execute(f"DELETE FROM Asociado WHERE cReserva='{reservation}' and cServicio='{service}'")
        else:
            # Eliminamos primero los asociados a dicha reserva
            for i in range(db.execute(f"""
            SELECT count(*) FROM Asociado where cReserva='{reservation}'
            """).fetchone()[0]):
                db.execute(f"DELETE FROM Asociado WHERE cReserva='{reservation}'")
            
            db.execute(f"DELETE FROM TieneReserva WHERE cReserva='{reservation}'")
            db.execute(f"DELETE FROM Reservas WHERE cReserva='{reservation}'")
        db.execute("COMMIT")
    
    bookings = db.execute("""
    SELECT * FROM Reservas NATURAL JOIN (SELECT * FROM TieneReserva) NATURAL JOIN (SELECT * FROM Asociado)
    """).fetchall()

    return render_template('table_bookings.html', bookings=bookings, reservation=reservation, dni=dni, service=service)

@app.route('/table_bookings', methods=['GET', 'POST'])
def table_bookings():
    db = get_db()

    # Capturar parámetros de consulta
    reservation = request.args.get('reservation', default='', type=str)
    dni = request.args.get('dni', default='', type=str)
    service = request.args.get('service', default='', type=str)

    bookings = db.execute("""
        SELECT * FROM Reservas NATURAL JOIN (SELECT * FROM TieneReserva) NATURAL JOIN (SELECT * FROM Asociado)
    """).fetchall()
    return render_template('table_bookings.html', bookings=bookings, reservation=reservation, dni=dni, service=service)

@app.route('/table_clients_bookings')
def table_clients_bookings():
    db = get_db()

    # Capturar parámetros de consulta
    reservation = request.args.get('reservation', default='', type=str)
    dni = request.args.get('dni', default='', type=str)
    service = request.args.get('service', default='', type=str)

    clients = db.execute("""
        SELECT * FROM Clientes
    """).fetchall()
    return render_template('table_clients_bookings.html', clients=clients, reservation=reservation, dni=dni, service=service)

@app.route('/table_transports_bookings')
def table_transports_bookings():
    db = get_db()

    # Capturar parámetros de consulta
    reservation = request.args.get('reservation', default='', type=str)
    dni = request.args.get('dni', default='', type=str)
    service = request.args.get('service', default='', type=str)

    transports = db.execute(
        """SELECT * FROM Transportes NATURAL JOIN (SELECT * FROM Servicios)"""
    ).fetchall()
    return render_template('table_transports_bookings.html', transports=transports, reservation=reservation, dni=dni, service=service)

@app.route('/table_activities_bookings')
def table_activities_bookings():
    db = get_db()

    # Capturar parámetros de consulta
    reservation = request.args.get('reservation', default='', type=str)
    dni = request.args.get('dni', default='', type=str)
    service = request.args.get('service', default='', type=str)

    activities = db.execute(
        """SELECT * FROM ActividadesTuristicas NATURAL JOIN (SELECT * FROM Servicios)"""
    ).fetchall()
    return render_template('table_activities_bookings.html', activities=activities, reservation=reservation, dni=dni, service=service)

@app.route('/table_accomodations_bookings')
def table_accomodations_bookings():
    db = get_db()

    # Capturar parámetros de consulta
    reservation = request.args.get('reservation', default='', type=str)
    dni = request.args.get('dni', default='', type=str)
    service = request.args.get('service', default='', type=str)

    accomodations = db.execute(
        """SELECT * FROM Alojamientos NATURAL JOIN (SELECT * FROM Servicios)"""
    ).fetchall()
    return render_template('table_accomodations_bookings.html', accomodations=accomodations, reservation=reservation, dni=dni, service=service)

import db
db.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
