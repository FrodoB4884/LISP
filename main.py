from flask import Flask, render_template
from routes import blueprints
from config import DB_PATH, HOST, PORT

def create_app():
    app = Flask(__name__)
    app.config['DB_PATH'] = DB_PATH

    # Register all blueprints
    for bp in blueprints:
        app.register_blueprint(bp)
    
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/manager')
    def manager():
        return render_template('manager.html')

    @app.route('/pos')
    def pos():
        return render_template('pos.html')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
