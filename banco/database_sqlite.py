#-----------------------
# BIBLIOTECAS
#-----------------------
import os
import sqlite3
from datetime import datetime
#-----------------------
# CLASSES
#-----------------------
class DataBaseSqlite():
    def __init__(self,nome:str="./data/rastreador.db") -> None:
        arquivo = os.path.basename(nome);
        pasta   = nome.replace(arquivo,'');
        if arquivo == '':
            arquivo = 'rastreador.db';
        if pasta == '':
            pasta = './data/';
        if(not(os.path.exists(pasta))):
            os.mkdir(pasta);
        if(not('/data/' in pasta)):
            self.nome = f'{pasta}/data/';
            os.mkdir(self.nome);
            self.nome = f'{self.nome}{arquivo}';
        else:
            self.nome = nome;
        self.__create_table();
    # -----------------------
    # OUTROS
    # -----------------------
    def __conexao(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.nome);
        return connection;
    
    @staticmethod
    def __dif_minutos(date1)->float:
        data_agora = datetime.now();
        date2      = data_agora.strftime('%Y-%m-%d %H:%M:%S');
        d1         = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S');
        d2         = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S');
        resultado  = d2-d1;
        minutes    = resultado.total_seconds();
        minutes    = float(minutes);
        return minutes;

    def __create_table(self,comando:str='') -> None:
        if(comando == ''):
            comando = ( "CREATE TABLE IF NOT EXISTS encomenda("
                        "id	INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "id_user 		INTEGER NOT NULL,"
                        "codigo			TEXT	NOT NULL,"
                        "nome_rastreio	TEXT	NOT NULL,"
                        "dia 			TEXT	NOT NULL,"
                        "informacoes    TEXT 	NOT NULL)");
        try:
            
            Connection = self.__conexao();
            cursor = Connection.cursor();
            cursor.execute(comando);
            Connection.commit();
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
        finally:
            if Connection:
                Connection.close();
    # -----------------------    
    # RASTREIO
    # -----------------------
    def verifica_rastreio(  self,comando:str='',
                            id_user:str='',
                            codigo:str='')->bool:
        if(id_user == '' or codigo == ''):
            return False;
        if(comando == ''):
            comando = ( "SELECT * "
                        "FROM encomenda "
                        f"WHERE id_user='{id_user}' "
                        f"AND codigo='{codigo}'");
        try:
            
            Connection = self.__conexao();
            cursor = Connection.cursor();
            cursor.execute(comando);
            tmp = cursor.fetchall();
            if tmp != []:
                cursor.close();
                return True;
            cursor.close();
            return False;
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
            return False;
        finally:
            if Connection:
                Connection.close();
    
    def insert_rastreio(self,comando:str='',tupla=[]) -> None:
        if(comando == ''):
            comando = ( "INSERT INTO encomenda "
                        "(id_user, codigo, nome_rastreio, "
                        "dia, informacoes) "
                        "VALUES(?,?,?,"
                        "(SELECT DATETIME('now','localtime')), ?) ");
        if(tupla == []):
            tupla = (   'id_user','codigo','nome_rastreio',
                        'dia','informacoes');
        if(self.verifica_rastreio(id_user=tupla[0],codigo=tupla[1])):
            return;
        try:
            Connection = self.__conexao();
            cursor = Connection.cursor();
            cursor.execute(comando, tupla);
            Connection.commit();
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
        finally:
            if Connection:
                Connection.close();
    
    def delete_rastreio(self,comando:str='',id_user:str='',
                        codigo:str='') -> None:
        if(id_user == '' or codigo == ''):
            return;
        if(comando == ''):
            comando = ( f"DELETE FROM encomenda "
                        f"WHERE id_user='{id_user}' "
                        f"AND codigo='{codigo}'");
        try:
            Connection = self.__conexao();
            cursor = Connection.cursor();
            cursor.execute(comando);
            Connection.commit();
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
        finally:
            if Connection:
                Connection.close();

    def select_rastreio(self,comando:str='',id_user:str=''):
        if(comando == ''):
            comando = ( f"SELECT informacoes, nome_rastreio "
                        f"FROM encomenda  WHERE id_user='{id_user}' "
                        f"ORDER BY id");
        try:
            Connection = self.__conexao();
            cursor     = Connection.cursor();
            cursor.execute(comando);
            data = cursor.fetchall();
            cursor.close();
            return data;
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
                return [];
        finally:
            if Connection:
                Connection.close();
    
    def atualiza_rastreio(self,comando:str=''):
        if(comando == ''):
            comando = ( "SELECT id_user, codigo, informacoes, "
                        "nome_rastreio FROM encomenda "
                        "ORDER BY dia LIMIT 1");
        try:
            Connection = self.__conexao();
            cursor     = Connection.cursor();
            cursor.execute(comando);
            data = cursor.fetchall();
            if data != []:
                id_user = str(data[0][0]);
                codigo  = str(data[0][1]);
                info    = str(data[0][2]);
                nome    = str(data[0][3]);
                cursor.close();
                return [id_user,codigo,info,nome];
            cursor.close();
            return [];
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
                return [];
        finally:
            if Connection:
                Connection.close();

    def validar_rastreio(self,comando:str='')->float:
        if(comando == ''):
            comando = ( "SELECT dia FROM encomenda "
                        "ORDER BY dia LIMIT 1");
        try:
            Connection = self.__conexao();
            cursor     = Connection.cursor();
            cursor.execute(comando);
            data = cursor.fetchall();
            if data != []:
                data = str(data[0][0]);
                data = self.__dif_minutos(data);
                cursor.close();
                return data;
            cursor.close();
            return -1;
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
                return -1;
        finally:
            if Connection:
                Connection.close();
    
    def update_rastreio(self,id_user:str='',codigo:str='',
                        comando:str='',informacoes:str='') -> bool:
        if(comando == ''):
            comando = ( f"UPDATE encomenda "
                        f"SET dia=(SELECT DATETIME"
                        f"('now','localtime')), " 
                        f"informacoes='{informacoes}' "
                        f"WHERE id_user='{id_user}' AND "
                        f"codigo='{codigo}'"
                        );
        try:
            Connection = self.__conexao();
            cursor     = Connection.cursor();
            cursor.execute(comando);
            Connection.commit();
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
        finally:
            if Connection:
                Connection.close();
    # -----------------------
#-----------------------
# MAIN()
#-----------------------
if(__name__ == "__main__"):
    pass;
#-----------------------