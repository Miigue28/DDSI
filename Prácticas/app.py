from flask import Flask, render_template, request, flash, redirect, url_for

# Create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'GRXViajes'

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/transports')
def transports():
    return render_template('transports.html')

@app.route('/reservations')
def reservation():
    return render_template('reservations.html')

@app.route('/clients', methods=['GET', 'POST'])
def clients():
    #if request.method == 'POST':
    #    dni = request.form['dni']
    #    name = request.form['name']
    #    surnames = request.form['surnames']
    #    email = request.form['email']
    #    
    #    db = get_db()
    #    db.execute(
    #        'INSERT INTO post (title, body, author_id)'
    #        ' VALUES (?, ?, ?)',
    #        (dni, name, surnames, email)
    #    )
    #    db.commit()
    #    return redirect(url_for('clients'))
    return render_template('clients.html')

@app.route('/employees')
def employees():
    return render_template('employees.html')

@app.route('/accomodations')
def accomodations():
    return render_template('accomodations.html')

@app.route('/activities')
def activities():
    return render_template('activities.html')

import db
db.init_app(app)

#from . import auth
#app.register_blueprint(auth.bp)

#from . import blog
#app.register_blueprint(blog.bp)
#app.add_url_rule('/', endpoint='index')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
