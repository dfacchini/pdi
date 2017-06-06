#-*- coding: utf-8 -*-
import kivy
kivy.require('1.9.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.image import Image
from kivy.garden.graph import Graph, MeshLinePlot
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

from core import Imagem
from menus import (
    MenuImagemDropDown,
    MenuFiltros,
    MenuOperadoresAritmeticos,
    MenuOperadoresLogicos
)


class MainLayout(BoxLayout):
    """
    Layout principal da aplicação.
    """

    caminho_temp = 'imagens/temp.jpg'
    imagem = ObjectProperty()
    imagem_secundaria = ObjectProperty()

    def __init__(self, *args, **kwargs):
        """
        Definição de atributos.
        """
        super(MainLayout, self).__init__(*args, **kwargs)
        self.menu_imagem = MenuImagemDropDown()

        self.menu_filtros = MenuFiltros()

        self.menu_operadores_aritmeticos = MenuOperadoresAritmeticos()
        self.menu_operadores_logicos = MenuOperadoresLogicos()

        self.imagem_core = None
        self.imagem_core_secundaria = None
        self.widgets_dinamicos = []
        self.carregar_imagem(u'imagens/dirty.png')
        self.carregar_imagem_secundaria(u'imagens/dirty.png')

    def recarregar_imagem(self):
        """
        Recarrega a imagem em tela.
        """
        self.salvar_imagem(caminho_imagem=self.caminho_temp)
        self.carregar_imagem(caminho_imagem=self.caminho_temp)

    def carregar_imagem(self, caminho_imagem):
        """
        Carrega uma imagem.
        """
        self.imagem.source = caminho_imagem
        self.imagem_core = Imagem(caminho_imagem)
        self.imagem.reload()

    def carregar_imagem_secundaria(self, caminho_imagem):
        """
        Carrega uma imagem.
        """
        self.imagem_secundaria.source = caminho_imagem
        self.imagem_core_secundaria = Imagem(caminho_imagem)
        self.imagem_secundaria.reload()

    def salvar_imagem(self, caminho_imagem):
        """
        Salva a imagem.
        """
        self.imagem_core.salvar(novo_caminho_imagem=caminho_imagem)

    def limpar(self):
        """
        Remove os widgets adicionados dinâmicamente.
        """
        for widget in self.widgets_dinamicos:
            self.remove_widget(widget)

    def mostrar_imagem_cinza(self):
        """
        Mostra a imagem em escala de cinza.
        """
        self.imagem_core.converter_escala_cinza()
        self.recarregar_imagem()

    def mostrar_imagem_equalizada(self):
        """
        Mostra a imagem equalizada.
        """
        self.imagem_core.equalizar_imagem()
        self.recarregar_imagem()

    def mostrar_histograma(self):
        """
        Mostra o histograma da imagem.
        """
        histograma = self.imagem_core.get_histograma()

        graph = Graph(
            xlabel='Tom de Cinza',
            ylabel='Quantidade de tons',
            padding=5,
            xmin=0,
            xmax=max(histograma.keys()),
            ymin=0,
            ymax=max(histograma.values())
        )
        plot = MeshLinePlot()
        plot.points = histograma.items()
        graph.add_plot(plot)
        self.widgets_dinamicos.append(graph)
        self.add_widget(graph)

    def aplicar_filtro(self, nome_filtro):
        """
        Aplica um filtro na imagem.
        """
        self.imagem_core.aplicar_filtro(nome_filtro=nome_filtro)
        self.recarregar_imagem()


class MainApp(App):
    """
    Aplicação.
    """

    def build(self):
        """
        Carrega a imagem na tela.
        """
        self.main_layout = MainLayout()
        return self.main_layout


if __name__ == '__main__':
    MainApp().run()
