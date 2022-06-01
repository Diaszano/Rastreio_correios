"""Conexão com o Banco de Dados SqLite"""
#-----------------------
# BIBLIOTECAS
#-----------------------
import os
import sys
import sqlite3
from typing import Union
from threading import Lock
from datetime import datetime
#-----------------------
# CONSTANTES
#-----------------------
#-----------------------
# CLASSES
#-----------------------
class DataBaseSqlite():
    def __init__(self) -> None:
        caminho = os.path.dirname(os.path.realpath('~/'));
        pasta   = os.path.join(caminho,"data");
        arquivo = "rastreador.db";
        if(not(os.path.exists(pasta))):
            os.mkdir(pasta);
        self.nome = os.path.join(pasta,arquivo);
        self.__create_table();
        self.__create_index();
        self.lock = Lock();
    # -----------------------
    # Funções estáticas
    # -----------------------
    @staticmethod
    def __dif_segundos(data:str) -> Union[int,float]:
        if((data == '') or (not isinstance(data,str))):
            return -1;
        data_agora = datetime.now();
        date2      = data_agora.strftime('%Y-%m-%d %H:%M:%S');
        d1         = datetime.strptime(data,'%Y-%m-%d %H:%M:%S');
        d2         = datetime.strptime(date2,'%Y-%m-%d %H:%M:%S');
        resultado  = d2-d1;
        segundos   = resultado.total_seconds();
        segundos   = float(segundos);
        return segundos;
    # -----------------------
    # Criação e conexão
    # -----------------------
    def __conexao(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.nome);
        return connection;
    
    def __create_index(self) -> None:
        comandos = [(   "CREATE INDEX IF NOT EXISTS "
                        "index_encomenda_id_user " 
                        "ON encomenda(id_user) "),
                    
                    (   "CREATE INDEX IF NOT EXISTS "
                        "index_encomenda_codigo "		
                        "ON encomenda(codigo)")];
        for comando in comandos:
            self.__execute_create(comando=comando);
        
    def __create_table(self) -> None:
        comandos = [(   "CREATE TABLE IF NOT EXISTS encomenda("
                        "id	INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "id_user 		TEXT    NOT NULL,"
                        "codigo			TEXT	NOT NULL,"
                        "nome_rastreio	TEXT	NOT NULL,"
                        "dia 			TEXT	NOT NULL,"
                        "informacoes    TEXT 	NOT NULL) ")];
        for comando in comandos:
            if(self.__execute_create(comando=comando) == False):
                sys.exit(0);
    
    def __execute_create(self,comando:str) -> Union[None,bool]:
        try:
            Connection = self.__conexao();
            cursor     = Connection.cursor();
            cursor.execute(comando);
            Connection.commit();
            cursor.close();
            return True;
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
            return False;
    # -----------------------
    # CRUD
    # -----------------------
    # Create
    def __insert(self,comando:str,tupla:tuple) -> None:
        self.lock.acquire();
        try:
            Connection = self.__conexao();
            cursor     = Connection.cursor();
            cursor.execute(comando, tupla);
            Connection.commit();
            cursor.close();
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
        self.lock.release();
    # Read
    def __select(self,comando:str) -> list:
        self.lock.acquire();
        try:
            Connection = self.__conexao();
            cursor     = Connection.cursor();
            cursor.execute(comando);
            retorno = cursor.fetchall();
            cursor.close();
            self.lock.release();
            return retorno;
        except sqlite3.Error as error:
            print("Falha do comando", error);
            if Connection:
                Connection.close();
            self.lock.release();
            return [];
    # Update
    def __update(self,comando:str) -> None:
        self.lock.acquire();
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
        self.lock.release();
    # Delete
    def __delete(self,comando:str) -> None:
        self.lock.acquire();
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
        self.lock.release();
    # -----------------------    
    # RASTREIO
    # -----------------------
    def insert_rastreio(self,tupla:tuple=[]) -> None:
        comando = ( " INSERT INTO encomenda "
                    " (id_user, codigo, nome_rastreio, "
                    " dia, informacoes) "
                    " VALUES(?, ?, ?, "
                    " (SELECT DATETIME('now','localtime')), ?)");
        if(not isinstance(tupla,tuple)):
            return;
        elif(len(tupla) != 4):
            # Exemplo de o que deveria vir
            # tupla = ( 'id_user',       'codigo',
            #           'nome_rastreio', 'informacoes');
            return;
        id_user = tupla[0];
        codigo  = tupla[1];
        if(self.__verifica_rastreio(id_user=id_user,codigo=codigo)):
            return;
        self.__insert(comando=comando,tupla=tupla);
    
    def __verifica_rastreio(self,id_user:str='',codigo:str='') -> bool:
        if((id_user == '') or (not isinstance(id_user,str))):
            return False;
        if((codigo == '') or (not isinstance(codigo,str))):
            return False;
        comando = ( f" SELECT * "
                    f" FROM encomenda "
                    f" WHERE id_user='{id_user}' "
                    f" AND codigo='{codigo}'");
        if(self.__select(comando=comando) == []):
            return False;
        return True;
    
    def select_rastreio(self,id_user:str='') -> list:
        if((id_user == '') or (not isinstance(id_user,str))):
            return;
        comando = ( f" SELECT informacoes, nome_rastreio, "
                    f" codigo FROM encomenda  "
                    f" WHERE id_user='{id_user}' "
                    f" ORDER BY id DESC ");
        return self.__select(comando=comando);

    def delete_rastreio(self,id_user:str='',codigo:str='') -> bool:
        if((id_user == '') or (not isinstance(id_user,str))):
            return False;
        if((codigo == '') or (not isinstance(codigo,str))):
            return False;
        comando = ( f" DELETE FROM encomenda "
                    f" WHERE id_user='{id_user}' "
                    f" AND codigo='{codigo}' ");
        if(self.__verifica_rastreio(id_user=id_user,codigo=codigo)):
            self.__delete(comando=comando);
            return True;
        return False;
    
    def atualiza_rastreio(self) -> list:
        comando = ( f" SELECT id_user, codigo, "
                    f" informacoes, nome_rastreio "
                    f" FROM encomenda ORDER BY dia "
                    f" LIMIT 1");
        dados = self.__select(comando=comando);
        if(dados != []):
            id_user = str(dados[0][0]);
            codigo  = str(dados[0][1]);
            info    = str(dados[0][2]);
            nome    = str(dados[0][3]);
            return [id_user,codigo,info,nome];
        return [];
    
    def validar_rastreio(self) -> Union[int,float]:
        comando = ( f" SELECT dia FROM encomenda "
                    f" ORDER BY dia LIMIT 1");
        dados = self.__select(comando=comando);
        if(dados != []):
            data = str(dados[0][0]);
            dif  = self.__dif_segundos(data);
            return dif;
        return -1;

    def update_rastreio(self,tupla:tuple=[]) -> None:
        if(not isinstance(tupla,tuple)):
            return;
        elif(len(tupla) != 3):
            # Exemplo de o que deveria vir
            # tupla = ('id_user', 'CPF', 'status',);
            return;
        id_user     = tupla[0];
        codigo      = tupla[1];
        informacoes = tupla[2];
        if((id_user == '') or (not isinstance(id_user,str))):
            return;
        if((codigo == '') or (not isinstance(codigo,str))):
            return;
        if((informacoes == '') or (not isinstance(informacoes,str))):
            return;
        comando = ( f" UPDATE encomenda "
                    f" SET dia=(SELECT DATETIME('now','localtime')), " 
                    f" informacoes='{informacoes}' "
                    f" WHERE id_user='{id_user}' "
                    f" AND codigo='{codigo}'");
        self.__update(comando=comando);
    # -----------------------
#-----------------------
# MAIN()
#-----------------------
if(__name__ == "__main__"):
    pass;
#-----------------------