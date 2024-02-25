from flask import Flask, jsonify, request
from flask_cors import CORS
from conexion.unionDB import DBHelper
from CrusOperation.Crudop import CRUDOperations
from CrusOperation.Crudemociones import CRUDEmociones
from Inteligencia.Consulta import InferenceService
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'Narusenin69'
CORS(app,  origins='http://localhost:3000')
jwt = JWTManager(app)

# Configuración de la base de datos
db_helper = DBHelper(server='DESKTOP-KUMMTSM', database='Grupo9_emociones3', username='sa', password='123456')

# Inicializar la clase CRUDOperations con el objeto DBHelper
crud_operations = CRUDOperations(db_helper)
crud_emociones = CRUDEmociones(db_helper)
inference_service = InferenceService()

# Endpoint create_new_usuario
@app.route('/api/usuarios', methods=['POST'])
def create_new_usuario():
    try:
        # Obtener datos del cuerpo de la solicitud
        nombre = request.form['nombre']
        correo_electronico = request.form['correo_electronico']
        contrasena = request.form['contrasena']
        fecha_nacimiento = request.form['fecha_nacimiento']
        pais = request.form['pais']
        materia_impartida = request.form['materia_impartida']
        foto_perfil_data = request.files['foto_perfil'].read()  # Leer la imagen como bytes

        # Conectar a la base de datos
        db_helper.connect()

        # Crear un nuevo usuario
        result = crud_operations.create_usuario(nombre, correo_electronico, contrasena, fecha_nacimiento, pais,
                                                materia_impartida, foto_perfil_data)

        # Devolver el resultado como respuesta
        return jsonify(result)

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

# Endpoint para eliminar un usuario por ID
@app.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def delete_usuario(id_usuario):
    try:
        # Conectar a la base de datos
        db_helper.connect()

        # Eliminar el usuario por ID
        crud_operations.delete_usuario(id_usuario)

        return jsonify({'message': 'Usuario eliminado correctamente'})

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

# Endpoint para actualizar un usuario por ID
@app.route('/api/usuarios/<int:id_usuario>', methods=['PUT'])
def update_usuario(id_usuario):
    try:
        # Conectar a la base de datos
        db_helper.connect()

        # Obtener datos del cuerpo de la solicitud
        nombre = request.form['nombre']
        correo_electronico = request.form['correo_electronico']
        fecha_nacimiento = request.form['fecha_nacimiento']
        pais = request.form['pais']
        materia_impartida = request.form['materia_impartida']
        foto_perfil_data = request.files['foto_perfil'].read()  # Leer la nueva imagen como bytes
        contrasena = request.form['contrasena']

        # Actualizar el usuario
        result = crud_operations.update_usuario(id_usuario, nombre, correo_electronico, fecha_nacimiento, pais, materia_impartida, foto_perfil_data, contrasena)

        return jsonify(result)

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

# Endpoint para obtener todos los usuarios
@app.route('/api/usuarios', methods=['GET'])
def get_all_usuarios():
    try:
        # Conectar a la base de datos
        db_helper.connect()

        # Obtener todos los usuarios
        usuarios = crud_operations.read_all_usuarios()

        # Devolver los usuarios como respuesta
        return jsonify(usuarios)

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

# Endpoint para obtener un usuario por su ID
@app.route('/api/usuarios/<int:id_usuario>', methods=['GET'])
def get_usuario(id_usuario):
    try:
        # Conectar a la base de datos
        db_helper.connect()

        # Obtener el usuario por su ID
        usuario = crud_operations.get_usuario_by_id(id_usuario)

        if usuario:
            return jsonify(usuario)
        else:
            return jsonify({'message': 'Usuario no encontrado'}), 404  # Devolver 404 si no se encuentra el usuario

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

# Endpoint para iniciar sesión
@app.route('/api/get_user_id', methods=['POST'])
def get_user_id():
    try:
        data = request.get_json()
        correo_electronico = data.get('correo_electronico')
        contrasena = data.get('contrasena')

        # Conectar a la base de datos y verificar las credenciales del usuario
        db_helper.connect()
        usuario = crud_operations.find_usuario_by_credentials(correo_electronico, contrasena)

        if usuario:
            # Si se encontró el usuario, devolver su ID en la respuesta
            return jsonify({'id_usuario': usuario['id_usuario']}), 200
        else:
            return jsonify({'error': 'Credenciales incorrectas'}), 401

    except Exception as ex:
        # Manejar otros errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión a la base de datos
        db_helper.close()

# Endpoint para obtener todas las emociones
@app.route('/api/emociones', methods=['GET'])
def get_all_emociones():
    try:
        # Conectar a la base de datos
        db_helper.connect()

        # Obtener todas las emociones
        emociones = crud_emociones.read_all_emociones()

        # Devolver las emociones como respuesta
        return jsonify(emociones)

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

# Endpoint para crear una nueva emocion
@app.route('/api/usuarios/<int:id_usuario>/emociones', methods=['POST'])
def create_emocion(id_usuario):
    try:
        db_helper.connect()

        data = request.json
        emociones_obtenidas = data.get('emociones_obtenidas')
        recomendacion = data.get('recomendacion')
        fecha_generacion = data.get('fecha_generacion')

        result = crud_emociones.create_emocion(id_usuario, emociones_obtenidas, recomendacion, fecha_generacion)

        return jsonify({"message": result})

    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

    finally:
        db_helper.close()

# Definimos el nuevo endpoint para obtener la recomendación
@app.route('/api/recomendacion', methods=['POST'])
def obtener_recomendacion():
    try:
        # Obtenemos los datos de la solicitud JSON
        data = request.json
        emociones_con_porcentajes = data.get('emociones_con_porcentajes')

        # Generamos la recomendación utilizando el servicio de inferencia
        recomendacion = inference_service.invoke(emociones_con_porcentajes)

        # Devolvemos la recomendación como respuesta JSON
        return jsonify({"recomendacion": recomendacion})

    except Exception as ex:
        # En caso de error, devolvemos un mensaje de error y código 500
        return jsonify({'error': str(ex)}), 500

# Endpoint para eliminar una emoción
@app.route('/api/emociones/<int:id_emocion>', methods=['DELETE'])
def delete_emocion(id_emocion):
    try:
        # Conectar a la base de datos
        db_helper.connect()

        # Eliminar la emoción
        result = crud_emociones.delete_emocion(id_emocion)

        return jsonify({"message": result})

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

#Endpoint para burcar emocion por usuario
@app.route('/api/usuarios/<int:id_usuario>/emociones', methods=['GET'])
def get_emociones_by_usuario(id_usuario):
    try:
        # Conectar a la base de datos
        db_helper.connect()

        # Obtener todas las emociones por usuario
        emociones = crud_emociones.read_emociones_by_usuario(id_usuario)

        # Devolver las emociones como respuesta
        return jsonify(emociones)

    except Exception as ex:
        # Manejar errores
        return jsonify({'error': str(ex)}), 500

    finally:
        # Cerrar la conexión
        db_helper.close()

if __name__ == '__main__':
    # Iniciar el servidor Flask
    app.run(debug=True)

    CORS(app)