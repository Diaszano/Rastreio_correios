#-----------------------
# BIBLIOTECAS
#-----------------------
import re
import requests
from banco.database_sqlite import DataBaseSqlite
#-----------------------
# CLASSES
#-----------------------
class Rastreio:
    @staticmethod
    def rastrear(codigo:str='')->str:
        if(len(codigo) != 13):
            return '';
        codigo = re.findall(r'(?P<Codigo>[a-z]{2}[0-9]{9}[a-z]{2})'
                            ,codigo,re.MULTILINE | re.IGNORECASE);
        if(codigo != []):
            codigo = codigo[0];
            url         = ( 'https://proxyapp.correios.com.br/v1/'
                            f'sro-rastro/{codigo}');
            informacoes = requests.get(url);
            informacoes = str(informacoes.text);
            regex:str   = ( r'(?P<Eventos>\"eventos\"\:)'
                            r'(?P<Dados_Eventos>\[.*?\])');
            informacoes = re.findall(   regex, informacoes,
                                        re.MULTILINE | re.IGNORECASE);
            if informacoes != []:
                informacoes = str(informacoes);
                regex:str   = r'(?P<Eventos>\{\"codigo\"\:.*?\.png\"\})*';
                informacoes = re.findall(   regex, informacoes, 
                                            re.MULTILINE | re.IGNORECASE);
                informacoes = ( valor 
                                for valor in informacoes 
                                if valor != '');
                informacoes = Rastreio.__limparMensagem(informacoes);
                return informacoes;
        return '';
    @staticmethod
    def __limparMensagem(eventos:list = []) -> list:
        rastreio = '';
        for resultado in eventos:
            dia       = '';
            tipo      = '';
            local     = '';
            destino   = '';
            detalhe   = '';
            descricao = '';
            if 'descricao' in resultado:
                temp      = re.findall('((\"descricao\"\:)(\".*?\"))', resultado, re.MULTILINE | re.IGNORECASE);
                temp      = str(temp[0][2]);
                temp      = temp.replace('"','');
                descricao = temp;
            if 'detalhe' in resultado:
                temp    = re.findall('((\"detalhe\"\:)(\".*?\"))', resultado, re.MULTILINE | re.IGNORECASE);
                temp    = temp[0][2];
                temp    = temp.replace('"','');
                detalhe = f'\n{temp}';
            if 'dtHrCriado' in resultado:
                temp = re.findall('((\"dtHrCriado\"\:)(\".*?\"))', resultado, re.MULTILINE | re.IGNORECASE);
                temp = temp[0][2]
                temp = temp.replace('"','');
                dia  = temp;
            if 'tipo' in resultado:
                tipo = re.findall('((\"tipo\"\:)(\"[^0-9]*?\"))', resultado, re.MULTILINE | re.IGNORECASE);
                if tipo != []:
                    temp = re.findall('(?:\"unidade\"\:\{\"endereco\"\:\{"cidade"\:)(\".*?\"),(?:\"uf\"\:)(\".*?\")', resultado, re.MULTILINE | re.IGNORECASE);
                    if temp != []:
                        temp        = temp[0];
                        [cidade,uf] = [temp[0],temp[1]];
                        uf          = uf.replace('"','');
                        cidade      = cidade.replace('"','');
                        local       = f'[{cidade}/{uf}]';
                    else:
                        temp  = re.findall('(?:\"unidade\"\:\{\"codSro\"\:\".*?\"(?:\,)\"endereco\"\:\{\}\,\"nome"\:)(\".*?\")', resultado, re.MULTILINE | re.IGNORECASE);
                        if temp != []:
                            temp  = temp[0].replace('"','');
                            local = f'[{temp}]';
            if '' in resultado:
                temp  = re.findall('(?:\"unidadeDestino\"\:\{\"endereco\"\:\{\"cidade\":)(\".*?\")(?:,\"uf\"\:)(\".*?\")', resultado, re.MULTILINE | re.IGNORECASE);
                if temp != []:
                    temp        = temp[0];
                    [cidade,uf] = [temp[0],temp[1]];
                    uf          = uf.replace('"','');
                    cidade      = cidade.replace('"','');
                    destino     = f' para [{cidade}/{uf}]';
            rastreio += f'[{Rastreio.__limpaData(dia)}] - {descricao} {local}{destino}{detalhe}\n\n\n';
        return rastreio;

    @staticmethod
    def __limpaData(data:str='')->str:
        ano      = data[:4];
        mes      = data[5:7];
        dia      = data[8:10];
        hora     = data[11:];
        mensagem = f"{dia}/{mes}/{ano} - {hora}";
        return mensagem;
#-----------------------
# Main()
#----------------------- 
if __name__ == '__main__':
    correios = Rastreio()
    resposta = correios.rastrear('');
    print(resposta);
    # tupla = ('05','','Celular',resposta)
    # #       ('id_user','codigo','nome_rastreio','data','informacoes');
    # print(resposta);
    # db = DataBase();
    # db.creat_table();
    # db.insert(comando_tuple=tupla);
    # # db.upadate(id_user='05',codigo='',mensagem=resposta)
#-----------------------    