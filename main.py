#-----------------------
# BIBLIOTECAS
#-----------------------
import re
import requests
from database import DataBase
#-----------------------
# CLASSES
#-----------------------
class rastreio:
    def __init__(self):
        pass;
    def rastrear(self,codigo:str='')->str:
        if(len(codigo) != 13):
            return '';
        codigo = re.findall(r'(?P<Codigo>[a-z]{2}[0-9]{9}[a-z]{2})',codigo,re.MULTILINE | re.IGNORECASE);
        if(codigo != []):
            codigo = codigo[0];
            url         = f'https://proxyapp.correios.com.br/v1/sro-rastro/{codigo}';
            informacoes = requests.get(url);
            informacoes = str(informacoes.text);
            informacoes = re.findall(r'(?P<Eventos>\"eventos\"\:)(?P<Dados_Eventos>\[.*?\])', informacoes, re.MULTILINE | re.IGNORECASE);
            if informacoes != []:
                informacoes = str(informacoes);
                informacoes = re.findall(r'(?P<Eventos>\{\"codigo\"\:.*?\.png\"\})*', informacoes, re.MULTILINE | re.IGNORECASE);
                informacoes = [valor for valor in informacoes if valor != ''];
                informacoes = self.limparMensagem(eventos=informacoes);
                return informacoes;
        return '';
    
    def limparMensagem(self,eventos:list = []) -> list:
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
            rastreio += f'[{self.limpaData(dia)}] - {descricao} {local}{destino}{detalhe}\n\n\n';
        return rastreio;

    def limpaData(self,data:str='')->str:
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
    correios = rastreio()
    resposta = correios.rastrear('LB526033530HK');
    tupla = ('05','LB526033530HK','Celular',resposta)
    #       ('id_user','codigo','nome_rastreio','data','informacoes');
    print(resposta);
    db = DataBase();
    db.creat_table();
    db.insert(comando_tuple=tupla);
    # db.upadate(id_user='05',codigo='LB526033530HK',mensagem=resposta)
#-----------------------    