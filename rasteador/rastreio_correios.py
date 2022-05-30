"""Rastreador"""
#-----------------------
# BIBLIOTECAS
#-----------------------
import re
import requests
#-----------------------
# CONSTANTES
#-----------------------
#-----------------------
# CLASSES
#-----------------------
class Rastreio:
    def __init__(self) -> None:
        regex               = ( r"(?P<Ano>[0-9]{4})(?:\-)"
                                r"(?P<Mes>[0-9]{2})(?:\-)"
                                r"(?P<Dia>[0-9]{2})(?:t)"
                                r"(?P<Hora>[0-9]{1,2})(?:\:)"
                                r"(?P<Minutos>[0-9]{1,2})(?:.*)");
        self.__re_dia       = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        regex               = r'((\"dtHrCriado\"\:)(\".*?\"))';
        self.__re_data      = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        regex               = r'((\"tipo\"\:)(\"[^0-9]*?\"))';
        self.__re_tipo      = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        regex               = r'((\"detalhe\"\:)(\".*?\"))';
        self.__re_detalhe   = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        regex               = r'((\"descricao\"\:)(\".*?\"))';
        self.__re_descricao = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        regex               = ( r'(?:\"unidade\"\:\{\"endereco\"\:\{'
                                r'"cidade"\:)(\".*?\"),(?:\"uf\"\:)'
                                r'(\".*?\")');
        self.__re_unidade_1 = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        regex               = ( r'(?:\"unidade\"\:\{\"codSro\"\:\".*?\"('
                                r'?:\,)\"endereco\"\:\{\}\,\"nome"\:)'
                                r'(\".*?\")');
        self.__re_unidade_2 = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        regex               = ( r'(?:\"unidadeDestino\"\:\{\"endereco\"\:'
                                r'\{\"cidade\":)(\".*?\")(?:,\"uf\"\:)'
                                r'(\".*?\")');
        self.__re_destino   = re.compile(   regex,re.MULTILINE|
                                            re.IGNORECASE);
        
        
    def rastrear(self,codigo:str='')->str:
        """Rastrear
        
        Aqui rastrearemos a encomenda.
        """
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
                informacoes = self.__limparMensagem(informacoes);
                return informacoes;
        return '';
    
    def __limparMensagem(self,eventos:list = []) -> list:
        rastreio          = [];
        for resultado in eventos:
            dia       = '';
            tipo      = '';
            local     = '';
            destino   = '';
            detalhe   = '';
            descricao = '';
            if 'descricao' in resultado:
                temp      = self.__re_descricao.findall(resultado);
                temp      = str(temp[0][2]);
                temp      = temp.replace('"','');
                descricao = temp;
            if 'detalhe' in resultado:
                temp    = self.__re_detalhe.findall(resultado);
                temp    = temp[0][2];
                temp    = temp.replace('"','');
                detalhe = f'\n{temp}';
            if 'dtHrCriado' in resultado:
                temp = self.__re_data.findall(resultado);
                temp = temp[0][2]
                temp = temp.replace('"','');
                dia  = temp;
            if 'tipo' in resultado:
                tipo = self.__re_tipo.findall(resultado);
                if tipo != []:
                    temp = self.__re_unidade_1.findall(resultado);
                    if temp != []:
                        temp        = temp[0];
                        [cidade,uf] = [temp[0],temp[1]];
                        uf          = uf.replace('"','');
                        cidade      = cidade.replace('"','');
                        local       = f'[{cidade}/{uf}]';
                    else:
                        temp  = self.__re_unidade_2.findall(resultado);
                        if temp != []:
                            temp  = temp[0].replace('"','');
                            local = f'[{temp}]';
            if 'unidadeDestino' in resultado:
                temp  = self.__re_destino.findall(resultado);
                if temp != []:
                    temp        = temp[0];
                    [cidade,uf] = [temp[0],temp[1]];
                    uf          = uf.replace('"','');
                    cidade      = cidade.replace('"','');
                    destino     = f' para [{cidade}/{uf}]';
            mensagem = (    f'[{self.__limpaData(dia,self.__re_dia)}] - '
                            f'{descricao} {local}{destino}'
                            f'{detalhe}\n\n\n');
            rastreio.append(mensagem);
        rastreio_str = '';
        tamanho_rastreio = len(rastreio)-1;
        for i in range(tamanho_rastreio+1):
            rastreio_str += rastreio[tamanho_rastreio - i];
        return rastreio_str;

    @staticmethod
    def __limpaData(data:str='',regex:re=None)->str:
        data = regex.findall(data);
        if(data != []):
            data     = data[0];
            if(len(data) == 5):
                ano      = data[0];
                mes      = data[1];
                dia      = data[2];
                hora     = data[3];
                minutos  = data[4];
                mensagem = f"{dia}/{mes}/{ano} - {hora}:{minutos}";
                return mensagem;
        return '';
#-----------------------
# FUNÇÕES()
#-----------------------
#-----------------------
# Main()
#----------------------- 
if __name__ == '__main__':
    pass;
#-----------------------    