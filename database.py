#-----------------------
# BIBLIOTECAS
#-----------------------
import os
import sqlite3
from datetime import datetime
#-----------------------
# CLASSES
#-----------------------
class DataBase():
    def __init__(self,nome:str="./data/database.db") -> None:
        arquivo = os.path.basename(nome);
        pasta   = nome.replace(arquivo,'');
        if arquivo == '':
            arquivo = 'database.db';
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

    def conexao(self) -> None:
        self.connection = sqlite3.connect(self.nome);
    
    def desconexao(self) -> None:
        try:
            self.connection.close();
        except:
            pass;
    
    def creat_table(self,comando:str='') -> None:
        if(comando == ''):
            comando =   """ CREATE TABLE IF NOT EXISTS encomenda(
                            id              INTEGER primary key autoincrement,
                            id_user         TEXT NOT NULL,
                            codigo          TEXT NOT NULL,
                            nome_rastreio   TEXT,
                            data            TEXT NOT NULL,
                            informacoes     TEXT NOT NULL)
                        """;
        try:
            self.conexao();
            Connection = self.connection;
            cursor = Connection.cursor();
            cursor.execute(comando);
            Connection.commit();
            # print("Comando efetuado com sucesso", cursor.rowcount);
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
        finally:
            if Connection:
                Connection.close();
                # print("Conexão com SQLite está fechada");

    def verifica(self,comando:str='',id_user:str='',codigo:str='')->bool:
        if(id_user == '' or codigo == ''):
            return False;
        if(comando == ''):
            comando =   f""" 
                            SELECT *
                            FROM encomenda
                            WHERE id_user='{id_user}' AND codigo='{codigo}'
                        """;
        try:
            self.conexao();
            Connection = self.connection;
            cursor = Connection.cursor();
            # print("Conexão com SQLite efetuada com sucesso");
            cursor.execute(comando);
            # print("Comando efetuado com sucesso", cursor.rowcount);
            if cursor.fetchall() != []:
                cursor.close();
                return True;
            cursor.close();
            return False;
        except sqlite3.Error as error:
            print("Falha do comando", error);
        finally:
            if Connection:
                Connection.close();
                # print("Conexão com SQLite está fechada");
    
    def insert(self,comando:str='',comando_tuple=[]) -> None:
        if(comando == ''):
            comando =   """ 
                            INSERT INTO encomenda
                            (id_user, codigo, nome_rastreio, 'data', informacoes)
                            VALUES(?, ?, ?,(SELECT DATETIME('now','localtime')), ?)
                        """;
        if(comando_tuple == []):
            comando_tuple = ('id_user','codigo','nome_rastreio','data','informacoes');
        if(self.verifica(id_user=comando_tuple[0],codigo=comando_tuple[1])):
            return;
        try:
            self.conexao();
            Connection = self.connection;
            cursor = Connection.cursor();
            # print("Conexão com SQLite efetuada com sucesso");
            cursor.execute(comando, comando_tuple);
            Connection.commit();
            # print("Comando efetuado com sucesso", cursor.rowcount);
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
        finally:
            if Connection:
                Connection.close();
                # print("Conexão com SQLite está fechada");

    def dif_minutos(self,date1):
        data_agora = datetime.now();
        date2      = data_agora.strftime('%Y-%m-%d %H:%M:%S');
        d1         = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S');
        d2         = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S');
        resultado  = d2-d1;
        minutes    = resultado.total_seconds() / 60;
        minutes    = int(minutes);
        return abs(minutes);

    def select(self,comando:str=''):
        if(comando == ''):
            comando =   f'SELECT id_user, codigo, informacoes, nome_rastreio FROM encomenda ORDER BY data LIMIT 1';
        try:
            self.conexao();
            Connection = self.connection;
            cursor = Connection.cursor();
            # print("Conexão com SQLite efetuada com sucesso");
            cursor.execute(comando);
            data = cursor.fetchall();
            # print("Comando efetuado com sucesso", cursor.rowcount);
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
            if Connection:
                Connection.close();
                return [];
                # print("Conexão com SQLite está fechada");

    def validar(self,comando:str=''):
        if(comando == ''):
            comando =   f'SELECT data FROM encomenda ORDER BY data LIMIT 1';
        try:
            self.conexao();
            Connection = self.connection;
            cursor = Connection.cursor();
            # print("Conexão com SQLite efetuada com sucesso");
            cursor.execute(comando);
            data = cursor.fetchall();
            # print("Comando efetuado com sucesso", cursor.rowcount);
            if data != []:
                data = str(data[0][0]);
                data = self.dif_minutos(data);
                cursor.close();
                return data;
            cursor.close();
            return 0;
        except sqlite3.Error as error:
            if Connection:
                Connection.close();
                return 0;
                # print("Conexão com SQLite está fechada");
    
    def update(self,id_user:str='',codigo:str='',comando:str='',mensagem:str='') -> bool:
        if(comando == ''):
            comando =   f""" UPDATE encomenda
                            SET 'data'=(SELECT DATETIME('now','localtime')), 
                            informacoes='{mensagem}'
                            WHERE id_user='{id_user}' AND codigo='{codigo}'
                        """;
        try:
            self.conexao();
            Connection = self.connection;
            cursor = Connection.cursor();
            # print("Conexão com SQLite efetuada com sucesso");
            cursor.execute(comando);
            Connection.commit();
            # print("Comando efetuado com sucesso", cursor.rowcount);
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
        finally:
            if Connection:
                Connection.close();
                # print("Conexão com SQLite está fechada");
#-----------------------
# MAIN()
#-----------------------
if(__name__ == "__main__"):
    db = DataBase();
    db.creat_table();
    db.validar()
#-----------------------