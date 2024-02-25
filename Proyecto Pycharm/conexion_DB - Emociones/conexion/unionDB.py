import pyodbc

class DBHelper:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        try:
            connection_string = f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
            self.connection = pyodbc.connect(connection_string)
            print('Conexión exitosa')
        except pyodbc.Error as ex:
            print(f'Error de pyodbc: {ex}')
            raise

    def close(self):
        if self.connection:
            self.connection.close()
            print('Conexión cerrada')
