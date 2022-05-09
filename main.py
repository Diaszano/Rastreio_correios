#-----------------------
# BIBLIOTECAS
#-----------------------
import os
import sys
import time
import threading
from database import *
from rastreio_correios import *
#-----------------------
# CONSTANTES
#-----------------------
ID_USER = 'User';
TEMPO_MAXIMO = 2;
#-----------------------
# FUNÇÕES
#-----------------------
def pausar_tela()->None:
    mensagem = f"\nDigite o enter para continuar!\n";
    input(mensagem);

def limpar_tela()->None:
    os.system("clear || cls");

def scanf_int(mensagem:str='')->int:
    limpar_tela();
    valor = input(mensagem);
    if not(valor.isdigit()):
        valor = scanf_int(mensagem=mensagem);
    return int(valor);

def scanf_str(mensagem:str='')->str:
    limpar_tela();
    valor = input(mensagem);
    if valor == '':
        valor = scanf_str(mensagem=mensagem);
    return str(valor);

def banco(db:DataBase=DataBase(),rastreador:Rastreio=Rastreio())->None:
    while True:
        if(db.validar_rastreio() >= TEMPO_MAXIMO):
            dados = db.atualiza_rastreio();
            if(dados != []):
                id_user = dados[0];
                codigo  = dados[1];
                informacoes = rastreador.rastrear(codigo=codigo);
                db.update_rastreio(id_user=id_user,codigo=codigo,informacoes=informacoes);
        elif(db.validar_rastreio() == 0):
            tempo_de_espera = TEMPO_MAXIMO * 60;
            tempo_de_espera = int(tempo_de_espera);
            # print(f"Tempo de espera = {tempo/60}");
            for _ in range(tempo_de_espera):
                time.sleep(1);
        else:
            tempo = TEMPO_MAXIMO * 60;
            tempo_de_espera = tempo - (db.validar_rastreio() * 60);
            tempo_de_espera = int(tempo_de_espera);
            # print(f"Tempo de espera = {tempo_de_espera/60}");
            for _ in range(tempo_de_espera):
                time.sleep(1);

def menu(rastreador:Rastreio=Rastreio(),db:DataBase=DataBase())->None:
    while True:
        opcao = 0;
        menu_print = (   "Opções de uso:"
                        "\n[1] - Rastrear encomenda"
                        "\n[2] - Listar encomendas"
                        "\n[3] - Deletar encomenda"
                        "\n[4] - Sair"
                        "\nSua opção: "
                    );
        while(opcao < 1 or opcao > 4):
            opcao = scanf_int(mensagem=menu_print);
        
        if(opcao == 1):
            codigo = [];
            while(codigo == []):
                mensagem = "Digite o código de rastreio ou -1 para sair: ";
                codigo   = scanf_str(mensagem=mensagem);
                if(codigo == '-1'):
                    menu(rastreador=rastreador,db=db);
                    return;
                codigo   = re.findall(r'(?P<Codigo>[a-z]{2}[0-9]{9}[a-z]{2})',codigo,re.MULTILINE | re.IGNORECASE);
                if codigo != []:
                    codigo   = str(codigo[0]).upper();
            mensagem = "Digite o nome do rastreio: ";
            nome     = scanf_str(mensagem=mensagem);
            informacoes = rastreador.rastrear(codigo=codigo);
            tupla = (ID_USER,codigo,nome,informacoes);
            db.insert_rastreio(tupla=tupla);
            opcao = 0;
        elif(opcao == 2):
            menu_print = (  "Opções de uso:"
                            "\n[1] - Mostar todas as informações"
                            "\n[2] - Mostar codigo e nome do rastreio"
                            "\nSua opção: "
                        );
            opcao = 0;
            while(opcao < 1 or opcao > 2):
                opcao = scanf_int(mensagem=menu_print);
                limpar_tela();
            resposta = f"Tu tens 📦 {len(db.select_rastreio(id_user=ID_USER))} encomendas guardadas\n";
            if(opcao == 1):
                resposta += f"#-----------------------#\n";
                for informacoes, nome in db.select_rastreio(id_user=ID_USER):
                    resposta += f"{informacoes} {nome}\n";
                    resposta += f"#-----------------------#\n";
            else:
                comando = f"SELECT codigo, nome_rastreio FROM encomenda WHERE id_user='{ID_USER}' ORDER BY id";
                for informacoes, nome in db.select_rastreio(comando=comando):
                    resposta += f"📦 {informacoes} {nome}\n";
            print(resposta);
            pausar_tela();
            opcao = 0;
        elif(opcao == 3):
            codigo = [];
            resposta = '';
            while(codigo == []):
                mensagem = "Digite o código de rastreio ou -1 para sair: ";
                codigo   = scanf_str(mensagem=mensagem);
                if(codigo == '-1'):
                    menu(rastreador=rastreador,db=db);
                codigo   = re.findall(r'(?P<Codigo>[a-z]{2}[0-9]{9}[a-z]{2})',codigo,re.MULTILINE | re.IGNORECASE);
                if codigo != []:
                    codigo   = str(codigo[0]).upper();
            if(db.verifica_rastreio(id_user=ID_USER,codigo=codigo)):
                db.delete_rastreio(id_user=ID_USER,codigo=codigo);
                resposta = f"Encomenda Deletada";
            else:
                resposta = f"Dados Inválidos";
            print(resposta);
            pausar_tela();
            opcao = 0;
        elif(opcao == 4):
            limpar_tela();
            return;
#-----------------------
# Main()
#----------------------- 
if __name__ == '__main__':
    db          = DataBase();
    rastreador  = Rastreio();
    db.creat_table();
    thread_banco = threading.Thread(target=banco, args=(db,rastreador,),daemon=True);
    thread_app   = threading.Thread(target=menu, args=(rastreador,db,));
    # Inicia a Thread
    thread_banco.start();
    thread_app.start();
    # Aguarda finalizar a Thread
    thread_app.join();
    sys.exit(0);
#-----------------------