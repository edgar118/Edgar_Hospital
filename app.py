
import json
from flask import Flask, jsonify, request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from datos import usuario, agregar_nota
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)
db = SQLAlchemy(app)

# conexion uri SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/hospital'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# modelos
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('user_type.id'))
    username = db.Column(db.String(80), nullable=False)
    identificacion = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(120))
    password = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(120))
    fecha_nacimiento = db.Column(db.String(120),)
    login = db.Column(db.Boolean, default=False)

class user_hospital_medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class user_type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class services(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    services_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    estado_salud = db.Column(db.String(120))
    observacion_medica = db.Column(db.String(120))

db.create_all()



#esquema logon
class loginSchema(ma.Schema):
    class Meta:
        fields = ("identificacion", "password", "login")
login_schema = loginSchema()
login_schema = loginSchema(many=True)

#LOGIN
@app.route('/login', methods=['POST'])
def inicio_sesion():  
    nuevo_login = {
        "identificacion": request.json['identificacion']
    }
    consulta = user.query.filter(user.identificacion.endswith(nuevo_login['identificacion']))[0]
    if nuevo_login['identificacion'] == consulta.identificacion:
        if  nuevo_login['password'] == consulta.password:
            if consulta.login == False:
                return 'Debes cambiar la contraseña'
    else:
        print("error en el login")
    return 'p'

#CAMBIO DE CONTRASEÑA 
@app.route('/cambiar/<int:identificacion>',methods=['PUT'])
def user_cambiar_contraseña(identificacion):
    nueva_contrasena = {
        "password": request.json['password'],
    }
    print(nueva_contrasena['password'])
    db.session.query(user).filter(user.identificacion == str(identificacion),user.login == False).update({'password':nueva_contrasena['password'],'login': True})
    db.session.commit()
    return 'sirvio?'
    


# REGISTRAR
@app.route('/usuarios/register', methods=['POST'])
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
    
    #SE VERIFICA EL TIPO DE DE USUARIO (HOSPITAL)
    if new_user['tipoUsuario'] == "Hospital":
        tipo = user_type.query.filter(user_type.name == 'Hospital').first()
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
            name_services = services(
                name=item,
                user_id=user_hospital.id
            )
            db.session.add(name_services)
            db.session.commit()

    #SE VERIFICA EL TIPO DE DE USUARIO (PACIENTE)
    elif new_user['tipoUsuario'] == "Paciente":
        tipo = user_type.query.filter(user_type.name == 'Paciente').first()
        user_paciente = user(
            username=new_user['nombre'],
            identificacion=new_user['identificacion'],
            direccion=new_user['direccion'],
            password=new_user['password'],
            fecha_nacimiento=new_user['fecha_de_nacimineto'],
            telefono=new_user['telefono'],
            email=new_user['email'],
            type_id=tipo.id
        )
        db.session.add(user_paciente)
        db.session.commit()
   
    #SE VERIFICA EL TIPO DE DE USUARIO (DOCTOR)
    elif new_user['tipoUsuario'] == "Doctor":
        user_Doctor = user_hospital_medico(
            username=new_user['nombre'],
            identificacion=new_user['identificacion'],
            direccion=new_user['direccion'],
            password=new_user['password'],
        )
        db.session.add(user_Doctor)
        db.session.commit()
    else:
        print("ERROR")
    return jsonify({"message": "user added"})



#AGREGAR DOCTOR
@app.route('/agregar_doctor', methods=['POST'])
def inicio_sesion_hospital():  
    nuevo_login = {
        "identificacion_hospi": request.json['identificacion_hospi']
    }
    identificacion_hospital = user.query.filter(user.identificacion.endswith(nuevo_login['identificacion_hospi']))[0]
    consulta = user_type.query.filter(user_type.name.endswith('Hospital'))[0]
    if nuevo_login['identificacion_hospi'] == identificacion_hospital.identificacion and identificacion_hospital.type_id == consulta.id:
        new_user = {
            "nombre": request.json['nombre'],
            "identificacion_doc": request.json['identificacion_doc'],
            "email": request.json['email'],
            "telefono": request.json['telefono'],
            "password": request.json['password'],
            "direccion": request.json['direccion']        
        }
        tipo = user_type.query.filter(user_type.name == 'Doctor').first()
        user_doctor = user(
            username=new_user['nombre'],
            identificacion=new_user['identificacion_doc'],
            password=new_user['password'],
            telefono=new_user['telefono'],
            email=new_user['email'],
            direccion=new_user['direccion'],
            type_id=tipo.id
        )
        db.session.add(user_doctor)
        db.session.commit()


        id_new_doc = user_doctor.id
        id_hospital = identificacion_hospital.id
        ingresar_relacion = user_hospital_medico(
            doc_id = id_new_doc,
            hospital_id = id_hospital
        )
        db.session.add(ingresar_relacion)
        db.session.commit()

    else:
        print("error en el login")
    return 'p'


#NOTAS
@app.route('/nota/<string:identificacion>',methods=['POST'])
def nota(identificacion):
    new_note = {    
        "estado_salud": request.json['estado_salud'],
        "observacion_medica": request.json['observacion_medica'],
        "id_doc": request.json['id_doc'],
        "id_paciente": request.json['id_paciente'],
        "id_servicio": request.json['id_servicio']
    }
    id_D = user.query.filter(user.id == new_note['id_doc']).first()
    id_P = user.query.filter(user.id == new_note['id_paciente']).first()
    id_servicio = services.query.filter(services.id == new_note['id_servicio']).first()
    nota = note(
        doc_id=id_D.id,
        patient_id=id_P.id,
        services_id=id_servicio.id,
        estado_salud=new_note['estado_salud'],
        observacion_medica=new_note['observacion_medica']
        )
    print(nota)
    db.session.add(nota)
    db.session.commit()
    return jsonify({"Registros": nota})




#FALTA TRAER LOS DATOS REQUERIDOS
class userSchema(ma.Schema):
    class Meta:
        fields = ("username", "identificacion", "telefono")
inst_schema = userSchema()
inst_schema = userSchema(many=True)
@app.route('/busqueda_notas')
def buscar_notas(): 
    datos = {    
        "identificacion": request.json['identificacion'],
    }
    consulta = user.query.filter(user.identificacion.endswith(datos['identificacion']))[0]
    tipo_usuario = user_type.query.filter(user_type.id==consulta.type_id)[0]
    print(tipo_usuario)
    if datos['identificacion']==consulta.identificacion:
        if tipo_usuario.name=='Paciente':
            id_consultor_paciente = consulta.id
            notas = note.query.filter(note.patient_id == id_consultor_paciente)
            print(notas)
            lista_notas = []
            for inten in notas:
                nota = {"estado salud": inten.estado_salud, "observacion medica":inten.observacion_medica}
                lista_notas.append(nota)
        elif tipo_usuario.name=='Doctor':
            id_consultor_doctor = consulta.id
            notas = note.query.filter(note.doc_id == id_consultor_doctor)
            print(notas)
            lista_notas = []
            for inten in notas:
                nota = {"estado salud": inten.estado_salud, "observacion medica":inten.observacion_medica}
                lista_notas.append(nota)
        elif tipo_usuario.name=='Hospital':
            id_consultor_hospital = consulta.id
            referencia_medicos = user_hospital_medico.query.filter(user_hospital_medico.hospital_id == id_consultor_hospital)
           
            lista_notas = []
            for inten in referencia_medicos:
                doctor_id = inten.doc_id
                notas = note.query.filter(note.doc_id == doctor_id)
                for int2 in notas:
                    nombre_medico = user.query.filter(user.id == doctor_id).first()
                    nota = {"nombre doctor": nombre_medico.username, "estado salud": int2.estado_salud, "observacion medica":int2.observacion_medica}
                    lista_notas.append(nota)


    return jsonify(lista_notas) 





if __name__ == '__main__':
    app.run(debug=True)

