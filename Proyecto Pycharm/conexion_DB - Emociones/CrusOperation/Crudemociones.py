import pyodbc
import datetime

class CRUDEmociones:
    def __init__(self, db_helper):
        self.db_helper = db_helper

#obtener todas las emociones
    def read_all_emociones(self):
        try:
            cursor = self.db_helper.connection.cursor()

            cursor.execute(
                "SELECT id_emocion, id_usuario, emociones_obtenidas, recomendacion, fecha_generacion FROM Emocion")

            emociones = cursor.fetchall()

            result = [{'id_emocion': row.id_emocion, 'id_usuario': row.id_usuario,
                       'emociones_obtenidas': row.emociones_obtenidas,
                       'recomendacion': row.recomendacion, 'fecha_generacion': row.fecha_generacion} for
                      row in emociones]

            return result

        except pyodbc.Error as ex:
            print(f'Error de pyodbc: {ex}')
            raise

        finally:
            cursor.close()

#crear emociones
    def create_emocion(self, id_usuario, emociones_obtenidas, recomendacion, nombre_reunion):
        try:
            fecha_generacion = datetime.datetime.now()  # Obtener la fecha actual
            cursor = self.db_helper.connection.cursor()

            cursor.execute("""
                INSERT INTO Emocion (id_usuario, emociones_obtenidas, recomendacion, fecha_generacion)
                VALUES (?, ?, ?, ?)
            """, (id_usuario, str(emociones_obtenidas), recomendacion, fecha_generacion))

            self.db_helper.connection.commit()

            return "Emoción creada exitosamente."

        except pyodbc.Error as ex:
            print(f'Error de pyodbc: {ex}')
            raise

        finally:
            cursor.close()

#CRUD para eliminar emociones
    def delete_emocion(self, id_emocion):
        try:
            cursor = self.db_helper.connection.cursor()

            # Eliminar emoción por su ID
            cursor.execute("DELETE FROM Emocion WHERE id_emocion = ?", (id_emocion,))

            # Confirmar la transacción
            self.db_helper.connection.commit()

            return 'Emoción eliminada exitosamente.'

        except pyodbc.Error as ex:
            print(f'Error de pyodbc: {ex}')
            raise

        finally:
            # Cerrar el cursor
            cursor.close()

#CRUD para buscar emociones por ID usuarios
    def read_emociones_by_usuario(self, id_usuario):
        try:
            cursor = self.db_helper.connection.cursor()

            # Obtener todas las emociones por usuario
            cursor.execute(
                "SELECT id_emocion, id_usuario, emociones_obtenidas, recomendacion, fecha_generacion FROM Emocion WHERE id_usuario = ?",
                id_usuario)

            emociones = cursor.fetchall()

            result = [{'id_emocion': row.id_emocion, 'id_usuario': row.id_usuario,
                       'emociones_obtenidas': row.emociones_obtenidas,
                       'recomendacion': row.recomendacion, 'fecha_generacion': row.fecha_generacion}
                      for row in emociones]

            return result

        except pyodbc.Error as ex:
            print(f'Error de pyodbc: {ex}')
            raise

        finally:
            # Cerrar el cursor
            cursor.close()