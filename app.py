from flask import Flask, jsonify, request
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
# view Login
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Usuário autenticado."})

    return jsonify({"message": "Credenciais incorretas."}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Usuário desconectado."})

@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Usuário cadastrado com sucesso."})
    
    return jsonify({"message": "As informações do usuário estão incompletas."}), 400

@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def get_user(id_user):
    user = User.query.get(id_user)

    if user:
        return jsonify({"username": user.username})
    
    return error_response(status_code=404)

@app.route("/user", methods=["GET"])
@login_required
def get_user_all():
    users = User.query.all()
    response = []
    if users[0]:
        for user in users:
            #response.append({"id": user.id, "username": user.username, "password": user.password})
            response.append(User.to_dict(user))

        return response
    
    return error_response(status_code=404, message="Nenhum usuário cadastrado.")

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    user = User.query.get(id_user)
    data = request.json
    new_password = data.get("password")

    if user and new_password:
        user.password = new_password
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} atualizado com sucesso."})
    
    return error_response(status_code=404, message=f"Usuário id {id_user} inexistente.")

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if id_user == current_user.id:
        return error_response(status_code=403, message="O usuário não pode excluir a si mesmo.")

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} excluído com sucesso."})
    
    return error_response(status_code=404, message=f"Usuário id {id_user} inexistente.")

def error_response(status_code, message="", id=0):
    response = f"Erro genérico."
    if status_code == 400:
        response = f"Informações incorretas."
    if status_code == 401:
        response = f"Usuário sem permissão."
    if status_code == 403:
        response = f"Ação não permitida."
    if status_code == 404:
        response =  f"Não encontrado."
    
    return jsonify({"message": f"{response} {message}"}), status_code

if __name__ == '__main__':
    app.run(debug=True)