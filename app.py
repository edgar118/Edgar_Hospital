
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datos import usuario,agregar_nota
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/hospital'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('user_type.id'))
    username = db.Column(db.String(80), unique=True, nullable=False)
    identificacion = db.Column(db.String(120), unique=True)
    email =  db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(120), nullable=False)
    fecha_nacimiento = db.Column(db.String(120),)

class user_hospital_medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class user_type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
class services(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
   
class note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    services_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    estado_salud = db.Column(db.String(120), unique=True)
    observacion_medica = db.Column(db.String(120), unique=True)

db.create_all()




#listar datos
@app.route('/usuarios')
def user_list():
    
    return jsonify({"message": "user added", "user": usuario})
    
#agregar datos
@app.route('/usuarios', methods=['POST'])
def adduser():
    new_user = {
        "tipoUsuario": request.json['tipoUsuario'],
        "nombre": request.json['nombre'],
        "identificacion": request.json['identificacion'],
        "email": request.json['email'],
        "telefono": request.json['telefono'],
        "password": request.json['password'],
        "direccion": request.json['direccion'],
        "servicios_medicos": request.json['servicios_medicos'],
        "fecha_de_nacimineto": request.json['fecha_de_nacimineto'],
        "estado_de_salud": request.json['estado_de_salud'],
        "observacion_medicas": request.json['observacion_medicas']
    }

    if new_user['tipoUsuario'] == "Hospital":
        tipo = user_type.query.filter(user_type.name=='Hospital').first()
        user_hospital = user(
            username=new_user['nombre'],
            identificacion=new_user['identificacion'],
            direccion=new_user['direccion'],
            password=new_user['password'],
            type_id=tipo.id
            )
        db.session.add(user_hospital)
        db.session.commit()
        for item in new_user['servicios_medicos']:
            name_services= services(
                name = item,
                user_id = user_hospital.id
            )
            db.session.add(name_services)
            db.session.commit()

    else:
        user_paciente = user(
            username=new_user['nombre'],
        )


    return jsonify({"message": "user added"})

#registrar ENDPOINT


#agregar datos doctor-paciente
@app.route('/agregar_doc', methods=['POST'])
def addnota():
    new_nota = {
        "id": request.json['id'],
        "nombre_M": request.json['nombre_M'],
        "servicios_medicos": request.json['servicios_medicos'],
        "nombre_P": request.json['nombre_P'],
        "estado_de_salud": request.json['estado_de_salud'],
        "observacion_medicas": request.json['observacion_medicas']
    }
    print(agregar_nota)
    agregar_nota.append(new_nota)
    return jsonify({"message": "product added", "user": agregar_nota})


#consulta mostrar
@app.route('/usuarios/<string:paciente>')
def buscar_mostrar(paciente):
    b_paciente=[datos for datos  in usuario if datos['id'] == paciente]
    if (len(b_paciente) >0):
        return jsonify(b_paciente[0]['nombre'],b_paciente[0]['direccion'],b_paciente[0]['servicios_medicos'],b_paciente[0]['observacion_medicas'])
    else:
         return jsonify({"message": "no found"})

#paciente
@app.route('/paciente/<string:paciente>')
def buscar_paciente(paciente):
    b_paciente=[datos for datos  in usuario if datos['id'] == paciente]
    if (len(b_paciente) >0):
        return jsonify({"message": "historial del paciente", "ojo":b_paciente[0]['observacion_medicas']})
    else:
         return jsonify({"message": "no found"})

#medicos
@app.route('/medicos/<string:paciente>')
def buscar_medicos(paciente):
    b_paciente=[datos for datos  in usuario if datos['id'] == paciente]
    if (len(b_paciente) >0):
        return jsonify(b_paciente[0]['nombre'],b_paciente[0]['observacion_medicas'],b_paciente[0]['estado_de_salud'])
    else:
         return jsonify({"message": "no found"})

#hospital
@app.route('/hospital/<string:paciente>')
def buscar_medicos2(paciente):
    b_paciente=[datos for datos  in usuario if datos['id'] == paciente]
    if (len(b_paciente) >0):
        return jsonify(b_paciente[0]['nombre'],b_paciente[0]['observacion_medicas'],b_paciente[0]['estado_de_salud'])
    else:
         return jsonify({"message": "no found"})

#agregar usuario bd
@app.route('/agregar_bd', methods=['POST'])
def agregar_bd_hospital():
    admin = user(username=(usuario[0]['nombre']), adrees=(usuario[0]['direccion']),service=(usuario[0]['servicios_medicos']))
    db.session.add(admin)
    db.session.commit()
    return 'sirvio'


if __name__ == '__main__':
    app.run(debug=True)
