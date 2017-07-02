#-*- coding: utf-8 -*-
from kivy.uix.dropdown import DropDown
from utils import LoadDialog, LoadDialogSec, SaveDialog


class Menu(DropDown):
    """
    Classe base de Menus.
    """

    def select(self, opcao, *args, **kwargs):
        """
        Executa a função de callback.
        """
        getattr(self, opcao)(*args, **kwargs)
        self.dismiss()

class MenuArquivoDropDown(Menu):
    def carregar_imagem(self):
        """
        Abre o popup para a escolha de uma nova imagem.
        """
        janela = LoadDialog()
        janela.popup.open()

    def carregar_imagem_secundaria(self):
        janela = LoadDialogSec()
        janela.popup.open()

    def salvar_imagem(self):
        """
        Abre o popup para a escolha do caminho para salvar a imagem.
        """
        janela = SaveDialog()
        janela.popup.open()
    def fechar(self):
        App.get_running_app().stop()

class MenuImagemDropDown(Menu):
    """
    Menu de Imagem.
    """
    def limpar(self, app):
        """
        Limpa a tela.
        """
        app.main_layout.limpar()

    def mostrar_imagem_cinza(self, app):
        """
        Mostra a imagem em escala de cinza.
        """
        app.main_layout.mostrar_imagem_cinza()

    def mostrar_imagem_equalizada(self, app):
        """
        Mostra a imagem equalizada.
        """
        app.main_layout.mostrar_imagem_equalizada()

    def mostrar_histograma(self, app):
        """
        Mostra o histograma da imagem.
        """
        app.main_layout.mostrar_histograma()


class MenuFiltros(Menu):
    """
    Menu dos filtros.
    """

    def aplicar_filtro(self, app, nome_filtro):
        """
        Executa a chamada para o filtro escolhido
        """
        app.main_layout.aplicar_filtro(nome_filtro=nome_filtro)


class MenuOperadoresAritmeticos(Menu):
    """
    Menu dos operadores aritméticos
    """
    def aplicar_operador(self, app, nome_operador):
        """
        Executa a chamada para o operador escolhido
        """
        app.main_layout.aplicar_operador_aritmetico(nome_operador=nome_operador)


class MenuOperadoresLogicos(Menu):
    """
    Menu dos operadores aritméticos
    """
    def aplicar_operador(self, app, nome_operador):
        """
        Executa a chamada para o operador escolhido
        """
        app.main_layout.aplicar_operador_logico(nome_operador)
