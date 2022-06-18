"""Rastreador"""
#-----------------------
# BIBLIOTECAS
#-----------------------
import re
import json
import requests
#-----------------------
# CONSTANTES
#-----------------------
#-----------------------
# CLASSES
#-----------------------
class Rastreio:
    @classmethod
    def __compile_re(cls) -> None:
        regex:str = (
            r'[a-z]{2}[0-9]{9}[a-z]{2}'
        );
        cls.__regex_codigo = re.compile(
            regex,
            re.MULTILINE |
            re.IGNORECASE
        );
        regex:str = ( 
            r'\{\"codigo\"\:.*?(?:(?:png\"\})'
            r'|(?:png\"\}\,)){1}'
        );
        cls.__regex_eventos = re.compile(
            regex,
            re.MULTILINE |
            re.IGNORECASE
        );
        regex:str = ( 
            r"(?P<Ano>[0-9]{4})(?:\-)"
            r"(?P<Mes>[0-9]{2})(?:\-)"
            r"(?P<Dia>[0-9]{2})(?:t)"
            r"(?P<Hora>[0-9]{1,2})(?:\:)"
            r"(?P<Minutos>[0-9]{1,2})(?:.*)"
        );
        cls.__regex_data = re.compile(   
            regex,
            re.MULTILINE |
            re.IGNORECASE
        );

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_isAlive'):
            cls.__compile_re();
            cls._isAlive = super().__new__(cls);
        return cls._isAlive;
    
    def rastrear(self,codigo:str='') -> str:
        """Rastrear
        
        Aqui rastrearemos a encomenda.
        """
        retorno_codigo:list[str] = self.__regex_codigo.findall(codigo);
        retorno       :str       = '';

        if(retorno_codigo != []):
            codigo:str = retorno_codigo[0];
            url   :str = (
                f'https://proxyapp.correios.com.br/'
                f'v1/sro-rastro/{codigo}'
            );
            
            retorno_get:requests.Response = requests.get(url);
            
            retorno_get_text:str = str(retorno_get.text);

            informacoes:list[str] = self.__regex_eventos.findall(
                retorno_get_text
            );
            
            for info in informacoes:
                retorno += self.__limparMensagem(info);
        return retorno;
    
    def __limparMensagem(self,evento:str = '') -> str:
        """Limpar Mensagem
        
        Aqui nós limparemos a mensagem e deixaremos do formato
        que fica muito mais legível.
        """ 
        data       :str  = '';
        local      :str  = '';
        destino    :str  = '';
        detalhe    :str  = '';
        descricao  :str  = '';
        retorno    :str  = '';
        evento_json:dict = json.loads(evento);
        
        if('descricao' in evento_json):
            descricao = evento_json['descricao'];
        if('detalhe' in evento_json):
            temp:str = evento_json['detalhe'];
            detalhe = f'\n{temp}';
        if('dtHrCriado' in evento_json):
            temp:str = evento_json['dtHrCriado'];
            data = self.__limpaData(
                data=temp,
                regex=self.__regex_data
            );
        if('unidade' in evento_json):
            temp:dict  = evento_json['unidade'];
            if('nome' in temp):
                pais:str = temp['nome'];
                local = f"[{pais}]";
            else:
                temp       = temp['endereco'];
                cidade:str = temp['cidade'];
                uf:str     = temp['uf'];
                local = f"[{cidade}/{uf}]";
        if('unidadeDestino' in evento_json):
            temp:dict  = evento_json['unidadeDestino'];
            temp       = temp['endereco'];
            if(('cidade' in temp) and ('uf' in temp)):
                cidade:str = temp['cidade'];
                uf:str     = temp['uf'];
                destino    = f' para [{cidade}/{uf}]';
        retorno = (
            f"[{data}] - {descricao} {local}{destino}"
            f"{detalhe}\n\n\n"
        );
        return retorno;

    @staticmethod
    def __limpaData(data:str='',regex:re=None) -> str:
        """Limpar Data
        
        Aqui nós limparemos a data e deixaremos do formato
        que fica muito mais legível.
        """ 
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