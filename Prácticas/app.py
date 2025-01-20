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

@app.route('/transports', methods=['GET', 'POST'])
def transports():
    db = get_db()
    if request.method == 'POST':
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
        error = None

        if db.execute(f"""
            SELECT count(*) FROM Servicios where cServicio='{codigo}'
        """).fetchone()[0] > 0:
            error = 'Código de transporte ya existente'

        if error is not None:
            flash(error)
        else:
            db.execute(f"insert into Servicios values('{codigo}', '{precio}', '{plazasTotales}', '{plazasLibres}')")
            db.execute(
                f"insert into Transportes values('{codigo}', '{tipo}', TO_DATE('{fecha}', 'YYYY-MM-DD HH24:MI'), '{compania}', '{origen}', '{destino}')"
            )
            db.execute("commit")
    
    transports = db.execute(
        """SELECT * FROM Transportes NATURAL JOIN (SELECT * FROM Servicios)"""
    ).fetchall()

    return render_template('transports.html',transports=transports)

@app.route('/reservations')
def reservation():
    return render_template('reservations.html')

@app.route('/clients', methods=['GET', 'POST'])
def clients():
    db = get_db()
    if request.method == 'POST':
        dni = request.form['dni']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        error = None

        if db.execute(f"""
            SELECT count(*) FROM Clientes where DNI='{dni}'
        """).fetchone()[0] > 0:
            error = 'Cliente ya existente'

        if error is not None:
            flash(error)
        else:
            db.execute(f"""
                INSERT INTO Clientes 
                VALUES('{dni}', '{name}', '{surname}', '{email}')
            """)
            db.execute("COMMIT")
    
    clients = db.execute("""
        SELECT * FROM Clientes
    """).fetchall()

    return render_template('clients.html', clients=clients)

@app.route('/employees')
def employees():
    return render_template('employees.html')

@app.route('/accomodations', methods=['GET', 'POST'])
def accomodations():
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

    return render_template('accomodations.html',accomodations=accomodations)

@app.route('/activities', methods=['GET', 'POST'])
def activities():
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

    return render_template('activities.html',activities=activities)

import db
db.init_app(app)


#from . import auth
#app.register_blueprint(auth.bp)

#from . import blog
#app.register_blueprint(blog.bp)
#app.add_url_rule('/', endpoint='index')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
