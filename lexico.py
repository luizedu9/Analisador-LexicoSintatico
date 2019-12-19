# -*- coding: utf-8 -*-

"""
P = {

    PROG -> programa id pvirg DECLS C-COMP
    DECLS -> & | variaveis LIST-DECLS
    LIST-DECLS -> DECL-TIPO D
    D -> & | LIST-DECLS
    DECL-TIPO -> LIST-ID dpontos TIPO pvirg
    LIST-ID -> id E
    E -> & | virg LIST-ID
    TIPO -> inteiro | real | logico | caracter
    C-COMP -> abrech LISTA-COMANDOS fechach
    LISTA-COMANDOS -> COMANDOS G
    G -> & | LISTA-COMANDOS
    COMANDOS -> IF | WHILE | READ | WRITE | ATRIB
    IF -> se abrepar EXPR fechapar C-COMP H
    H -> & | senao C-COMP
    WHILE -> enquanto abrepar EXPR fechapar C-COMP
    READ -> leia abrepar LIST-ID fechapar pvirg
    ATRIB -> id atrib EXPR pvirg
    WRITE -> escreva abrepar LIST-W fechapar pvirg
    LIST-W -> ELEM-W L
    L -> & | virg LIST-W
    ELEM-W -> EXPR | cadeia
    EXPR -> SIMPLES P
    P -> & | oprel SIMPLES
    SIMPLES -> TERMO R
    R -> & | opad SIMPLES
    TERMO -> FAT S
    S -> & | opmul TERMO
    FAT -> id | cte | abrepar EXPR fechapar | verdadeiro | falso | opneg FAT

    Tokens:

    ID, CTE, CADEIA, PROGRAMA, VARIAVEIS, INTEIRO, REAL, LOGICO, 
    CARACTER, SE, SENAO, ENQUANTO, LEIA, ESCREVA, FALSO, VERDADEIRO,
    ATRIB, OPREL, OPAD, OPMUL, OPNEG, PVIRG, DPONTOS, VIRG, ABREPAR, 
    FECHAPAR, ABRECH, FECHACH.

    Comentarios:

    // linha
    /* bloco */
}
"""

from os import path
import sys

class TipoToken:
    PROGRAMA = (1, 'programa')
    VARIAVEIS = (2, 'variaveis')
    INTEIRO = (3, 'inteiro')
    REAL = (4, 'real')
    LOGICO = (5, 'logico')
    CARACTER = (6, 'caracter')
    SE = (7, 'se')
    SENAO = (8, 'senao')
    ENQUANTO = (9, 'enquanto')
    LEIA = (10, 'leia')
    ESCREVA = (11, 'escreva')
    FALSO = (12, 'falso')
    VERDADEIRO = (13, 'verdadeiro')
    ID = (14, 'id')
    CTE = (15, 'constante')
    CADEIA = (16, 'cadeia')
    ATRIB = (17, ':=')
    OPREL = (18, 'relacional')
    OPAD = (19, '+-')
    OPMUL = (20, '*/')
    OPNEG = (21, '!')
    PVIRG = (22, ';')
    DPONTOS = (23, ':')
    VIRG = (24, ',')
    ABREPAR = (25, '(')
    FECHAPAR = (26, ')')
    ABRECH = (27, '{')
    FECHACH = (28, '}')
    FIMARQ = (29, 'fim_arquivo')
    ERROR = (30, 'error')

class Token:
    def __init__(self, tipo, lexema, linha):
        self.tipo = tipo
        (const, msg) = tipo
        self.const = const
        self.msg = msg
        self.lexema = lexema
        self.linha = linha

class Lexico:

    reservadas = { 'programa': TipoToken.PROGRAMA, 'variaveis': TipoToken.VARIAVEIS,
        'inteiro': TipoToken.INTEIRO, 'real': TipoToken.REAL, 'logico': TipoToken.LOGICO,
        'caracter': TipoToken.CARACTER, 'se': TipoToken.SE, 'senao': TipoToken.SENAO,
        'enquanto': TipoToken.ENQUANTO, 'leia': TipoToken.LEIA, 'escreva': TipoToken.ESCREVA,
        'falso': TipoToken.FALSO, 'verdadeiro': TipoToken.VERDADEIRO }

    def __init__(self, nome_arquivo):
        self.nome_arquivo = nome_arquivo
        self.arquivo = None

    def abre_arquivo(self):
        if not self.arquivo is None:
            print('ERRO: Arquivo em uso')
            exit()
        elif path.exists(self.nome_arquivo):
            self.arquivo = open(self.nome_arquivo, "r", encoding="utf-8")
            self.buffer = ''
            self.linha = 1
        else:
            print('ERRO: Arquivo ' + self.nome_arquivo + ' inexistente.')
            exit()

    def fecha_arquivo(self):
        if self.arquivo is None:
            print('ERRO: Arquivo não encontrado')
            exit()
        else:
            self.arquivo.close()

    def get_char(self):
        if self.arquivo is None:
            print('ERRO: Arquivo não encontrado')
            exit()
        elif len(self.buffer) > 0:
            char = self.buffer[0]
            self.buffer = self.buffer[1:]
            return char
        else:
            char = self.arquivo.read(1)
            # se nao foi eof, pelo menos um char foi lido
            # senao len(c) == 0
            if len(char) == 0:
                return None
            else:
                return char.lower()

    def unget_char(self, char):
        if not char is None:
            self.buffer = self.buffer + char

    def get_token(self):
        lexema = ''
        estado = 1
        char = None
        while (True):

            if estado == 1:
                # estado inicial que faz primeira classificacao
                char = self.get_char()
                if char is None:
                    return Token(TipoToken.FIMARQ, '<eof>', self.linha)
                elif char in {' ', '\t', '\n'}: # Ignorar
                    if char == '\n':
                        self.linha = self.linha + 1
                elif char.isalpha(): # Identificador
                    estado = 2
                    cont = 1
                elif char == '"': # String
                    lexema = char
                    estado = 3   
                elif char.isdigit(): # Digito
                    estado = 4
                elif char in {':', '=', '<', '>', '+', '-', '*', '!', ';', ',', '(', ')', '{', '}'}: # Simbolos (exceto /)
                    estado = 5
                elif char == '/': # Divisão ou comentario
                    estado = 6
                else:
                    return Token(TipoToken.ERROR, '<' + char + '>', self.linha)
            
            elif estado == 2: # (Identificadores), (Palavras reservadas)
                # (aux123, a1), (programa, se) 
                lexema = lexema + char
                char = self.get_char()
                cont += 1
                if char is None or (not char.isalnum()): # Se encontrou caracter diferente de letra ou numero
                    self.unget_char(char)
                    if cont > 32:
                        return Token(TipoToken.ERROR, '<' + lexema + '>', self.linha)
                    elif lexema in Lexico.reservadas:
                        return Token(Lexico.reservadas[lexema], lexema, self.linha)
                    else:
                        return Token(TipoToken.ID, lexema, self.linha)

            elif estado == 3: # (Strings)
                # (" Alguma coisa ")
                char = self.get_char()
                if char is None: # Retorna erro se chegou em final de arquivo.
                    return Token(TipoToken.ERROR, '<' + lexema + '>', self.linha)
                elif char == '"': # Retorna valores entre " "
                    lexema = lexema + char
                    return Token(TipoToken.CADEIA, lexema, self.linha)
                else: # Concatena caracteres
                    lexema = lexema + char
            
            elif estado == 4: # (INTEIRO), (REAL)
                # (1, 4852), (5.7, 7164.4124)
                lexema = lexema + char
                char = self.get_char()
                if char == '.':
                    estado == 'apos_ponto'
                elif char is None or (not char.isdigit()):
                    self.unget_char(char)
                    return Token(TipoToken.CTE, lexema, self.linha)

            elif estado == 'apos_ponto': # Trata o digito após ponto
                lexema = lexema + char
                char = self.get_char()
                if char is None or (not char.isdigit()):
                    self.unget_char(char)
                    return Token(TipoToken.CTE, lexema, self.linha)
            
            elif estado == 5: # (Simbolo)
                if char == ':': # (:=), (:)
                    char = self.get_char()
                    if char == '=':
                        return Token(TipoToken.ATRIB, ':=', self.linha)
                    else:
                        self.unget_char(char)
                        return Token(TipoToken.DPONTOS, ':', self.linha)
                elif char == '=':
                    return Token(TipoToken.OPREL, '=', self.linha)
                elif char == '<': # (<=), (<>), (<)
                    char = self.get_char()
                    if char == '=':
                        return Token(TipoToken.OPREL, '<=', self.linha)
                    elif char == '>':
                        return Token(TipoToken.OPREL, '<>', self.linha)
                    else:
                        self.unget_char(char)
                        return Token(TipoToken.OPREL, '<', self.linha)
                elif char == '>': # (>=), (>)
                    char = self.get_char()
                    if char == '=':
                        return Token(TipoToken.OPREL, '>=', self.linha)
                    else:
                        self.unget_char(char)
                        return Token(TipoToken.OPREL, '>', self.linha)
                elif char == '+':
                    return Token(TipoToken.OPAD, '+', self.linha)
                elif char == '-':
                    return Token(TipoToken.OPAD, '-', self.linha)
                elif char == '*':
                    return Token(TipoToken.OPMUL, '*', self.linha)
                elif char == '!':
                    return Token(TipoToken.OPNEG, '!', self.linha)
                elif char == ';':
                    return Token(TipoToken.PVIRG, ';', self.linha)
                elif char == ',':
                    return Token(TipoToken.VIRG, ',', self.linha)
                elif char == '(':
                    return Token(TipoToken.ABREPAR, '(', self.linha)
                elif char == ')':
                    return Token(TipoToken.FECHAPAR, ')', self.linha)
                elif char == '{':
                    return Token(TipoToken.ABRECH, '{', self.linha)
                elif char == '}':
                    return Token(TipoToken.FECHACH, '}', self.linha)
            
            elif estado == 6: # (Comentario), (Divisão)
                # (//, /* alguma coisa */), (/)
                char = self.get_char()
                if char == '/': # Ignora até o final da linha
                    while (not char is None) and (char != '\n'):
                        char = self.get_char()
                    self.unget_char(char)
                    estado = 1
                elif char == '*': # Ignora até encontrar */
                    while (True):
                        char = self.get_char()
                        if char == '*':
                            char = self.get_char()
                            if char == '/':
                                estado = 1
                                break
                            else:
                                self.unget_char(char)
                        if char == None:
                            return Token(TipoToken.ERROR, '</*>', self.linha)

                else: # Divisão
                    return Token(TipoToken.OPMUL, '/', self.linha)

if __name__== "__main__":

   arquivo = sys.argv[1]
   lex = Lexico(arquivo)
   lex.abre_arquivo()
   while(True):
       token = lex.get_token()
       print('token = ' + token.msg + ', lexema = ' + token.lexema + ', linha = ' + str(token.linha))
       if token.const == TipoToken.FIMARQ[0]:
           break
   lex.fecha_arquivo()
