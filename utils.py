#-*- coding: utf-8 -*-
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

class Janela(FloatLayout):
    """
    Janela base para carregar/salvar uma imagem.
    """
    titulo = ''

    def __init__(self, *args, **kwargs):
        """
        Configura o Popup.
        """
        super(Janela, self).__init__(*args, **kwargs)
        self.popup = Popup(
            title=self.titulo,
            content=self,
            size_hint=(0.9, 0.9)
        )

    def fechar(self):
        """
        Fecha a janela.
        """
        self.popup.dismiss()


class LoadDialog(Janela):
    """
    Carrega uma imagem.
    """
    titulo = u'Carregar Imagem'

    def carregar(self, app, caminho_arquivo):
        """
        Carrega a imagem em tela.
        """
        app.main_layout.carregar_imagem(caminho_arquivo[0])
        self.fechar()


class LoadDialogSec(Janela):
    """
    Carrega uma imagem.
    """
    titulo = u'Carregar Imagem Secundária'

    def carregar(self, app, caminho_arquivo):
        """
        Carrega a imagem em tela.
        """
        app.main_layout.carregar_imagem_secundaria(caminho_arquivo[0])
        self.fechar()


class SaveDialog(Janela):
    """
    Salva uma imagem.
    """
    titulo = 'Salvar Imagem'

    def salvar(self, app, diretorio, nome):
        """
        Salva uma imagem no disco.
        """
        app.main_layout.salvar_imagem('%s/%s' % (diretorio, nome))
        self.fechar()
