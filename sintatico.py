# -*- coding: utf-8 -*-

"""
P = {
    A -> prog $
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

import sys

from lexico import TipoToken as tt, Token, Lexico

class Sintatico:

    def __init__(self):
        self.lex = None
        self.token_atual = None
        self.tabela_simbolo = { 'PROGRAMA': 0, 'VARIAVEIS': 1, 'INTEIRO': 2, 'REAL': 3 , 'LOGICO': 4, 'CARACTER': 5, 'SE': 6,
        'SENAO': 7, 'ENQUANTO': 8, 'LEIA': 9, 'ESCREVA': 10, 'FALSO': 11, 'VERDADEIRO': 12 }
        self.tabela_follow = { 
            'PROG': [tt.FIMARQ[0]],
            'DECLS': [tt.ABRECH[0]],
            'LIST_DECLS': [tt.ABRECH[0]],
            'D': [tt.ABRECH[0]],
            'DECL_TIPO': [tt.ID[0], tt.ABRECH[0]],
            'LIST_ID': [tt.FECHAPAR[0], tt.DPONTOS[0]], 
            'E': [tt.FECHAPAR[0], tt.DPONTOS[0]],
            'TIPO': [tt.PVIRG[0]], 
            'C_COMP': [tt.FIMARQ[0], tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.SENAO[0], tt.FECHACH[0]],
            'LISTA_COMANDOS': [tt.FECHACH[0]], 
            'G': [tt.FECHACH[0]], 
            'COMANDOS': [tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.FECHACH[0]],
            'IF': [tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.FECHACH[0]], 
            'H': [tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.FECHACH[0]],
            'WHILE': [tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.FECHACH[0]],
            'READ': [tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.FECHACH[0]],
            'ATRIB': [tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.FECHACH[0]],
            'WRITE': [tt.ENQUANTO[0], tt.ESCREVA[0], tt.ID[0], tt.LEIA[0], tt.SE[0], tt.FECHACH[0]],
            'LIST_W': [tt.FECHAPAR[0]],
            'L': [tt.FECHAPAR[0]],
            'ELEM_W': [tt.FECHAPAR[0], tt.VIRG[0]],
            'EXPR': [tt.FECHAPAR[0], tt.VIRG[0], tt.PVIRG[0]],
            'P': [tt.FECHAPAR[0], tt.VIRG[0], tt.PVIRG[0]],
            'SIMPLES': [tt.FECHAPAR[0], tt.VIRG[0], tt.PVIRG[0], tt.OPREL[0]],
            'R': [tt.FECHAPAR[0], tt.VIRG[0], tt.PVIRG[0], tt.OPREL[0]],
            'TERMO': [tt.FECHAPAR[0], tt.VIRG[0], tt.PVIRG[0], tt.OPAD[0], tt.OPREL[0]],
            'S': [tt.FECHAPAR[0], tt.VIRG[0], tt.PVIRG[0], tt.OPAD[0], tt.OPREL[0]],
            'FAT': [tt.OPAD[0], tt.OPMUL[0]],
            }

    def interprete(self, arquivo):
        if not self.lex is None:
            print('ERRO: Já existe um arquivo sendo processado.')
        else:
            self.lex = Lexico(arquivo)
            self.lex.abre_arquivo()
            self.token_atual = self.lex.get_token()

            self.A()
            self.consome( tt.FIMARQ )

            self.lex.fecha_arquivo()

    def atual_igual(self, token):
        (const, msg) = token
        return self.token_atual.const == const

    def consome(self, token):
        if self.atual_igual( token ):
            self.token_atual = self.lex.get_token()
            if self.token_atual.const == tt.ID[0] and (self.token_atual.lexema not in self.tabela_simbolo):
                self.tabela_simbolo[self.token_atual.lexema] = (self.token_atual.const, 
                    self.token_atual.msg, self.token_atual.linha)
        else:
            (const, msg) = token
            self.erro( msg )

    def erro(self, esperado):
        print('ERRO DE SINTAXE [linha %d]: era esperado "%s" mas veio "%s"'
           % (self.token_atual.linha, esperado, self.token_atual.lexema))
        raise

    def sincroniza(self, follow):
        #print(follow)
        follow_list = self.tabela_follow[follow]
        while True:
            #print(self.token_atual.lexema)
            self.token_atual = self.lex.get_token()
            if self.token_atual.const in follow_list: # SINCRONIZOU
                #print(self.token_atual.lexema)
                break
        
    def A(self):
        try:
            self.PROG()
            self.consome( tt.FIMARQ )
        except:
            quit()

    def PROG(self):
        try:
            self.consome( tt.PROGRAMA )
            self.consome( tt.ID )
            self.consome( tt.PVIRG )
            self.DECLS()
            self.C_COMP()
        except:
            self.sincroniza('PROG')

    def DECLS(self):
        try:
            if self.atual_igual( tt.VARIAVEIS ):
                self.consome( tt.VARIAVEIS )
                self.LIST_DECLS()
            else:
                pass
        except:
            self.sincroniza('DECLS')

    def LIST_DECLS(self):
        try:
            self.DECL_TIPO()
            self.D()
        except:
            self.sincroniza('LIST_DECLS')

    def D(self):
        try:    
            if self.atual_igual( tt.ID ):
                self.LIST_DECLS()
            else:
                pass
        except:
            self.sincroniza('D')

    def DECL_TIPO(self):
        try:
            self.LIST_ID()
            self.consome( tt.DPONTOS )
            if self.TIPO():
                self.erro( 'tipo' )
            self.consome( tt.PVIRG )
        except:
            self.sincroniza('DECL_TIPO')

    def LIST_ID(self):
        try:
            self.consome( tt.ID )
            self.E()
        except:
            self.sincroniza('LIST_ID')

    def E(self):
        try:
            if self.atual_igual( tt.VIRG ):
                self.consome( tt.VIRG )
                self.LIST_ID()
            else:
                pass
        except:
            self.sincroniza('E')
    
    def TIPO(self):
        try:
            if self.atual_igual( tt.INTEIRO ):
                self.consome( tt.INTEIRO )
            elif self.atual_igual( tt.REAL ):
                self.consome( tt.REAL )
            elif self.atual_igual( tt.LOGICO ):
                self.consome( tt.LOGICO )
            elif self.atual_igual( tt.CARACTER ):
                self.consome( tt.CARACTER )
            else:
                return True
        except:
            self.sincroniza('TIPO')

    def C_COMP(self):
        try:
            self.consome( tt.ABRECH )
            self.LISTA_COMANDOS()
            self.consome( tt.FECHACH )
        except:
            self.sincroniza('C_COMP')
    
    def LISTA_COMANDOS(self):
        try:
            if self.COMANDOS():
                self.erro( 'comando' )
            self.G()
        except:
            self.sincroniza('LISTA_COMANDOS')

    def G(self):
        try:
            if self.atual_igual( tt.SE ) or self.atual_igual( tt.ENQUANTO ) or self.atual_igual( tt.LEIA ) or self.atual_igual( tt.ESCREVA ) or self.atual_igual( tt.ID ):
                self.LISTA_COMANDOS()
            else:
                pass
        except:
            self.sincroniza('G')
    
    def COMANDOS(self):
        try:
            if self.atual_igual( tt.SE ):
                self.IF()
            elif self.atual_igual( tt.ENQUANTO ):
                self.WHILE()
            elif self.atual_igual( tt.LEIA ):
                self.READ()
            elif self.atual_igual( tt.ESCREVA ):
                self.WRITE()
            elif self.atual_igual( tt.ID ):
                self.ATRIB()
            else:
                return True
        except:
            self.sincroniza('COMANDOS')
    
    def IF(self):
        try:
            self.consome( tt.SE )
            self.consome( tt.ABREPAR )
            self.EXPR()
            self.consome( tt.FECHAPAR )
            self.C_COMP()
            self.H()
        except:
            self.sincroniza('IF')
    
    def H(self):
        try:
            if self.atual_igual( tt.SENAO ):
                self.consome( tt.SENAO )
                self.C_COMP()
            else:
                pass
        except:
            self.sincroniza('H')

    def WHILE(self):
        try:
            self.consome( tt.ENQUANTO )
            self.consome( tt.ABREPAR )
            self.EXPR()
            self.consome( tt.FECHAPAR )
            self.C_COMP()
        except:
            self.sincroniza('WHILE')
    
    def READ(self):
        try:
            self.consome( tt.LEIA )
            self.consome( tt.ABREPAR )
            self.LIST_ID()
            self.consome( tt.FECHAPAR )
            self.consome( tt.PVIRG )
        except:
            self.sincroniza('READ')
    
    def ATRIB(self):
        try:
            self.consome( tt.ID )
            self.consome( tt.ATRIB )
            self.EXPR()
            self.consome( tt.PVIRG )
        except:
            self.sincroniza('ATRIB')
    
    def WRITE(self):
        try:
            self.consome( tt.ESCREVA )
            self.consome( tt.ABREPAR )
            self.LIST_W()
            self.consome( tt.FECHAPAR )
            self.consome( tt.PVIRG )
        except:
            self.sincroniza('WRITE')
    
    def LIST_W(self):
        try:
            if self.ELEM_W():
                self.erro( 'expreção ou cadeia' )
            self.L()
        except:
            self.sincroniza('LIST_W')
    
    def L(self):
        try:
            if self.atual_igual( tt.VIRG ):
                self.consome( tt.VIRG )
                self.LIST_W()
            else:
                pass
        except:
            self.sincroniza('L')

    def ELEM_W(self):
        try:
            if self.atual_igual( tt.ID ) or self.atual_igual( tt.CTE ) or self.atual_igual( tt.ABREPAR ) or self.atual_igual( tt.VERDADEIRO ) or self.atual_igual( tt.FALSO ) or self.atual_igual( tt.OPNEG ):
                self.EXPR()
            elif self.atual_igual( tt.CADEIA ):
                self.consome( tt.CADEIA )
            else:
                return True
        except:
            self.sincroniza('ELEM_W')
    
    def EXPR(self):
        try:
            self.SIMPLES()
            self.P()
        except:
            self.sincroniza('EXPR')
    
    def P(self):
        try:
            if self.atual_igual( tt.OPREL ):
                self.consome( tt.OPREL )
                self.SIMPLES()
            else:
                pass
        except:
            self.sincroniza('P')
    
    def SIMPLES(self):
        try:
            self.TERMO()
            self.R()
        except:
            self.sincroniza('SIMPLES')
    
    def R(self):
        try:
            if self.atual_igual( tt.OPAD ):
                self.consome( tt.OPAD )
                self.SIMPLES() 
            else:
                pass
        except:
            self.sincroniza('R')

    def TERMO(self):
        try:
            if self.FAT():
                self.erro( 'FAT' ) 
            self.S()
        except:
            self.sincroniza('TERMO')

    def S(self):
        try:
            if self.atual_igual( tt.OPMUL ):
                self.consome( tt.OPMUL )
                self.TERMO() 
            else:
                pass
        except:
            self.sincroniza('S')

    def FAT(self):
        try:
            if self.atual_igual( tt.ID ):
                self.consome( tt.ID )
            elif self.atual_igual( tt.CTE ):
                self.consome( tt.CTE )
            elif self.atual_igual( tt.ABREPAR ):
                self.consome( tt.ABREPAR )
                self.EXPR()
                self.consome( tt.FECHAPAR )
            elif self.atual_igual( tt.VERDADEIRO ):
                self.consome( tt.VERDADEIRO )
            elif self.atual_igual( tt.FALSO ):
                self.consome( tt.FALSO )
            elif self.atual_igual( tt.OPNEG ):
                self.consome( tt.OPNEG )
                if self.FAT():
                    self.erro( 'FAT' )  
            else:
                return True 
        except:
            self.sincroniza('FAT')   

if __name__== "__main__":
    arquivo = sys.argv[1]
    tabela_cont = 13
    parser = Sintatico()
    parser.interprete(arquivo)
    try: # Tenta utilizar o parametro -t
        if sys.argv[2] == '-t':
            with open(sys.argv[3], 'w') as file:
                file.write(str(parser.tabela_simbolo))
    except:
        pass