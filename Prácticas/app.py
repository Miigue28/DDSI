from flask import Flask, render_template

# Create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'GRXViajes'

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/transports')
def transports():
    return render_template('transports.html')

#from . import db
#db.init_app(app)

#from . import auth
#app.register_blueprint(auth.bp)

#from . import blog
#app.register_blueprint(blog.bp)
#app.add_url_rule('/', endpoint='index')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)