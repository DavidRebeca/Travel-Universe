from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes import routes_bp

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/travel-universe-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secretdiscret'
db.init_app(app)

app.register_blueprint(routes_bp)

if __name__ == '__main__':
    app.run()
