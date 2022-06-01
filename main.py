#-----------------------
# BIBLIOTECAS
#-----------------------
import re
import os
import sys
import time
import threading
from rasteador import Rastreio
from banco import DataBaseSqlite
#-----------------------
# CONSTANTES
#-----------------------
ID_USER = 'User';
TEMPO_MAXIMO = 2;
#-----------------------
# CLASSES
#-----------------------
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

def banco(  db:DataBaseSqlite=DataBaseSqlite(),
            rastreador:Rastreio=Rastreio())->None:
    while True:
        tempo_banco = db.validar_rastreio();
        if((tempo_banco) == -1):
            tempo           = TEMPO_MAXIMO * 60;
            tempo_de_espera = tempo;
            if tempo_de_espera > 0:
                # print(f"Tempo de espera = {tempo_de_espera/60}");
                time.sleep(tempo_de_espera);
        elif((tempo_banco/60) >= TEMPO_MAXIMO):
            dados = db.atualiza_rastreio();
            if(dados != []):
                id_user = dados[0];
                codigo  = dados[1];
                informacoes = rastreador.rastrear(codigo=codigo);

                tupla = (id_user,codigo,informacoes);
                db.update_rastreio(tupla=tupla);
        else:
            tempo           = TEMPO_MAXIMO * 60;
            tempo_de_espera = tempo - tempo_banco;
            if tempo_de_espera > 0:
                # print(f"Tempo de espera = {tempo_de_espera/60}");
                time.sleep(tempo_de_espera);

def menu(   rastreador:Rastreio=Rastreio(),
            db:DataBaseSqlite=DataBaseSqlite())->None:
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
                mensagem = ("Digite o código de rastreio ou -1 para "
                            "sair: ");
                codigo   = scanf_str(mensagem=mensagem);
                if(codigo == '-1'):
                    menu(rastreador=rastreador,db=db);
                    return;
                regex = r'(?P<Codigo>[a-z]{2}[0-9]{9}[a-z]{2})';
                codigo   = re.findall(  regex,codigo,
                                        re.MULTILINE|re.IGNORECASE);
                if codigo != []:
                    codigo   = str(codigo[0]).upper();
            mensagem = "Digite o nome do rastreio: ";
            nome     = scanf_str(mensagem=mensagem);
            regex = r'(?P<Nome>.{1,30})';
            nome   = re.findall(regex,nome,
                                re.MULTILINE|re.IGNORECASE);
            if nome != []:
                nome   = str(nome[0]).title();
            else:
                nome = "";
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
            resposta = (f"Tu tens 📦 "
                        f"{len(db.select_rastreio(id_user=ID_USER))} "
                        f"encomendas guardadas\n");
            if(opcao == 1):
                resposta += f"#-----------------------#\n";
                for informacoes, nome, codigo in db.select_rastreio(
                                            id_user=ID_USER):
                    resposta = (f"{informacoes}Encomenda: "
                                f"{codigo} {nome}\n");
                    resposta += f"#-----------------------#\n";
            else:
                for _ ,nome ,codigo in db.select_rastreio(
                                            id_user=ID_USER):
                    resposta += f"📦 {codigo} {nome}\n";
            print(resposta);
            pausar_tela();
            opcao = 0;
        elif(opcao == 3):
            codigo = [];
            resposta = '';
            while(codigo == []):
                mensagem = ("Digite o código de rastreio ou -1 para "
                            "sair: ");
                codigo   = scanf_str(mensagem=mensagem);
                if(codigo == '-1'):
                    menu(rastreador=rastreador,db=db);
                regex    = r'(?P<Codigo>[a-z]{2}[0-9]{9}[a-z]{2})';
                codigo   =  re.findall(regex,codigo,
                            re.MULTILINE|re.IGNORECASE);
                if codigo != []:
                    codigo   = str(codigo[0]).upper();
            if(db.delete_rastreio(id_user=ID_USER,codigo=codigo)):
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
    db          = DataBaseSqlite();
    rastreador  = Rastreio();
    thread_banco = threading.Thread(target=banco, 
                                    args=(db,rastreador,),
                                    daemon=True);
    thread_app   = threading.Thread(target=menu, args=(rastreador,db,));
    # Inicia a Thread
    thread_banco.start();
    thread_app.start();
    # Aguarda finalizar a Thread
    thread_app.join();
    sys.exit(0);
#-----------------------