#-*- coding: utf-8 -*-
from collections import defaultdict
from decimal import Decimal
from PIL import Image
import operator


class Imagem(object):
    """
    Abstração de uma Imagem.
    """

    def __init__(self, caminho_imagem, *args, **kwargs):
        """
        Inicialização da classe.
        """
        self.caminho_imagem = caminho_imagem
        self.imagem = Image.open(caminho_imagem).convert("RGB")
        self.pixels = self.imagem.load()
        self.filtros = [
            Filtros(imagem=self),
            PassaAlta(imagem=self),
            Mediana(imagem=self),
            Moda(imagem=self),
            Robert(imagem=self)
        ]

        try:
            self.imagem.width, self.imagem.height = self.imagem.size
        except AttributeError:
            pass

        self.quantidade_pixels = (
            Decimal(self.imagem.height * self.imagem.width)
        )
        super(Imagem, self).__init__(*args, **kwargs)

    def _get_xy(self, x_inicio=0, y_inicio=0, x_final=None, y_final=None):
        """
        Retorna um generator das coordenadas (x, y) da imagem.
        """
        x_final = x_final or self.imagem.width
        y_final = y_final or self.imagem.height

        for x in range(x_inicio, x_final):
            for y in range(y_inicio, y_final):
                yield (x, y)

    def _get_yx(self, x_inicio=0, y_inicio=0, x_final=None, y_final=None):
        """
        Retorna um generator das coordenadas (x, y) da imagem.
        """
        x_final = x_final or self.imagem.width
        y_final = y_final or self.imagem.height

        for y in range(y_inicio, y_final):
            for x in range(x_inicio, x_final):
                yield (x, y)

    def _get_probabilidades(self, histograma):
        """
        Retorna as probabilidades para cada nível de cinza do histograma da
        imagem original.
        """
        probabilidades = defaultdict(lambda: 0)
        for tom_cinza, quantidade in histograma.iteritems():
            probabilidades[tom_cinza] = quantidade / self.quantidade_pixels
        return probabilidades

    def _get_novos_tons_cinza(self, probabilidades):
        """
        :return: Um dicionário do tipo: {tom_cinza: novo_tom_cinza}

        Retorna os novos tons de cinza que devem ser aplicados.
        """
        g = defaultdict(lambda: 0)
        probabilidade_acumulada = 0
        for tom_cinza, probabilidade in probabilidades.items():
            probabilidade_acumulada += probabilidade
            novo_tom_cinza = probabilidade_acumulada * 255
            g[tom_cinza] = int(Decimal(novo_tom_cinza).quantize(0))
        return g

    def salvar(self, novo_caminho_imagem=None):
        """
        Salva a imagem.
        """
        caminho_imagem = novo_caminho_imagem or self.caminho_imagem
        self.imagem.save(caminho_imagem)

    def converter_escala_cinza(self):
        """
        Converte uma imagem para escala de cinza.
        """
        for x, y in self._get_xy():
            pixel = self.pixels[x, y]
            r, g, b = self.pixels[x, y]
            tom_cinza = int(0.3 * r + 0.59 * g + 0.11 * b)
            self.pixels[x, y] = (tom_cinza, tom_cinza, tom_cinza)
        return self.pixels

    def get_histograma(self):
        """
        :return: {tom_cinza: quantidade_pixels, ...}

        Retorna o histograma da imagem.
        """
        histograma = defaultdict(lambda: 0)
        for x, y in self._get_xy():
            r, g, b = self.pixels[x, y]
            histograma[r] += 1
        return histograma

    def equalizar_imagem(self):
        """
        Equaliza a imagem em escala de cinza.
        """
        histograma = self.get_histograma()
        probabilidades = self._get_probabilidades(histograma)
        novos_tons = self._get_novos_tons_cinza(probabilidades)

        for x, y in self._get_xy():
            r, g, b = self.pixels[x, y]
            tom_cinza = novos_tons[r]
            self.pixels[x, y] = (tom_cinza, tom_cinza, tom_cinza)

    def aplicar_filtro(self, nome_filtro, *args, **kwargs):
        """
        Aplica um filtro na imagem.
        """
        for filtro in self.filtros:
            if hasattr(filtro, nome_filtro):
                getattr(filtro, nome_filtro)(*args, **kwargs)
                break

    def aplicar_logico(self, operador, *args, **kwargs):
        """
        Aplica um filtro na imagem.
        """
        if hasattr(self, operador):
            getattr(self, operador)(*args, **kwargs)


    def operador_and(self, imagem_secundaria):

        x_final=self.imagem.width
        y_final=self.imagem.height

        x_final_2 = imagem_secundaria.imagem.width
        y_final_2 = imagem_secundaria.imagem.height

        generator = self._get_xy(
            x_final=x_final,
            y_final=y_final,
        )

        for x, y in generator:

            if x < x_final_2 and y < y_final_2:
                pixel_resultante = self.pixels[x, y][0] & imagem_secundaria.pixels[x, y][0]
                self.pixels[x, y] = (pixel_resultante, pixel_resultante, pixel_resultante)

    def operador_xor(self, imagem_secundaria):

        x_final=self.imagem.width
        y_final=self.imagem.height

        x_final_2 = imagem_secundaria.imagem.width
        y_final_2 = imagem_secundaria.imagem.height

        generator = self._get_xy(
            x_final=x_final,
            y_final=y_final,
        )

        for x, y in generator:

            if x < x_final_2 and y < y_final_2:
                pixel_resultante = self.pixels[x, y][0] ^ imagem_secundaria.pixels[x, y][0]
                self.pixels[x, y] = (pixel_resultante, pixel_resultante, pixel_resultante)

    def operador_or(self, imagem_secundaria):

        x_final=self.imagem.width
        y_final=self.imagem.height

        x_final_2 = imagem_secundaria.imagem.width
        y_final_2 = imagem_secundaria.imagem.height

        generator = self._get_xy(
            x_final=x_final,
            y_final=y_final,
        )

        for x, y in generator:

            if x < x_final_2 and y < y_final_2:
                pixel_resultante = self.pixels[x, y][0] | imagem_secundaria.pixels[x, y][0]
                self.pixels[x, y] = (pixel_resultante, pixel_resultante, pixel_resultante)

class Filtros(object):
    """
    Filtros que podem ser aplicados na imagem.
    """

    # Filtros Passa-Baixas / Correlação, Convolução
    matriz_filtro = [
        [1.5/18, 2.0/18, 1.5/18],
        [2.0/18, 4.0/18, 2.0/18],
        [1.5/18, 2.0/18, 1.5/18],
    ]

    # matriz_filtro = [
    #     [1.0/10, .5/10, 1.5/10],
    #     [1.0/10, 0.5/10, 1.5/10],
    #     [0.5/10, 1.5/10, 1.5/10],
    # ]

    # matriz_filtro = [
    #     [1.0/94, 2.0/94, 4.0/94, 2.0/94, 1.0/94],
    #     [2.0/94, 4.0/94, 8.0/94, 4.0/94, 2.0/94],
    #     [4.0/94, 8.0/94, 10.0/94, 8.0/94, 4.0/94],
    #     [2.0/94, 4.0/94, 8.0/94, 4.0/94, 2.0/94],
    #     [1.0/94, 2.0/94, 4.0/94, 2.0/94, 1.0/94],
    # ]

    def __init__(self, imagem):
        """
        """
        self.imagem = imagem

    def correlacao(self, rotacionar_matriz_180=False):
        """
        Aplica o filtro de correlação.
        """
        # Limita a aplicação da técnica para pontos que possuem vizinhos.
        qtd_linhas_espaco = len(self.matriz_filtro) - 2
        generator = self.imagem._get_xy(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=self.imagem.imagem.width - qtd_linhas_espaco,
            y_final=self.imagem.imagem.height - qtd_linhas_espaco,
        )

        j = (0, 1, 2)
        if rotacionar_matriz_180:
            j = (2, 1, 0)

        for x, y in generator:
            soma = 0
            for i in range(0, 3):
                soma += self.imagem.pixels[x-1+i, y-1][0] * self.matriz_filtro[i][j[0]]
                soma += self.imagem.pixels[x-1+i, y][0] * self.matriz_filtro[i][j[1]]
                soma += self.imagem.pixels[x-1+i, y+1][0] * self.matriz_filtro[i][j[2]]
            soma = int(soma)
            self.imagem.pixels[x, y] = (soma, soma, soma)

    def convolucao(self):
        """
        Aplica o filtro de convolução.
        """
        self.correlacao(rotacionar_matriz_180=True)


class PassaAlta(Filtros):

    matriz_filtro = [
        [-0.5, -0.5, -0.5],
        [-0.5, 4.0, -0.5],
        [-0.5, -0.5, -0.5]
    ]

    # matriz_filtro = [
    #     [-1.0, -1.0, -1.0, -1.0, -1.0],
    #     [-1.0, 1.0, 1.0, 1.0, -1.0],
    #     [-1.0, 1.0, 8.0, 1.0, -1.0],
    #     [-1.0, 1.0, 1.0, 1.0, -1.0],
    #     [-1.0, -1.0, -1.0, -1.0, -1.0],
    # ]
    # matriz_filtro = [
    #     [-1.0, -1.0, -1.0],
    #     [0.0, 0.0, 0.0],
    #     [1.0, 1.0, 1.0]
    # ]

    def passa_alta(self):
        """
        Aplica filtros de passa_alta
        """
        # Limita a aplicação da técnica para pontos que possuem vizinhos.
        qtd_linhas_espaco = len(self.matriz_filtro) - 2

        x_final=self.imagem.imagem.width - qtd_linhas_espaco
        y_final=self.imagem.imagem.height - qtd_linhas_espaco

        generator = self.imagem._get_xy(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=x_final,
            y_final=y_final,
        )

        j = (0, 1, 2)
        matriz_aux = {x:{y:(0,0,0) for y in range(y_final + 1)} for x in range(x_final + 1)}

        for x, y in generator:
            soma = 0
            for i in range(0, 3):
                soma += self.imagem.pixels[x-1+i, y-1][0] * self.matriz_filtro[i][j[0]]
                soma += self.imagem.pixels[x-1+i, y][0] * self.matriz_filtro[i][j[1]]
                soma += self.imagem.pixels[x-1+i, y+1][0] * self.matriz_filtro[i][j[2]]

            # Para valores negativos considerar sempre 0 ou somar 255.
            soma = int(soma)
            if soma < 0:
                soma = 0

            matriz_aux[x][y] = (soma, soma, soma)
            # self.imagem.pixels[x, y] = (soma, soma, soma)

        for x in range(x_final + 1):
            matriz_aux[x][y_final] = self.imagem.pixels[x, y_final]
            matriz_aux[x][0] = self.imagem.pixels[x, 0]

        for y in range(y_final + 1):
            matriz_aux[x_final][y] = self.imagem.pixels[x_final, y]
            matriz_aux[0][y] = self.imagem.pixels[0, y]


        generator = self.imagem._get_yx(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=self.imagem.imagem.width - qtd_linhas_espaco,
            y_final=self.imagem.imagem.height - qtd_linhas_espaco,
        )

        for x, y in generator:
            soma = 0
            for i in range(0, 3):
                try:
                    soma += matriz_aux[x-1+i][y-1][0] * self.matriz_filtro[i][j[0]]
                    soma += matriz_aux[x-1+i][y][0] * self.matriz_filtro[i][j[1]]
                    soma += matriz_aux[x-1+i][y+1][0] * self.matriz_filtro[i][j[2]]
                except:
                    from IPython import embed; embed()

            # Para valores negativos considerar sempre 0 ou somar 255.
            soma = int(soma)
            if soma < 0:
                soma = 0

            self.imagem.pixels[x, y] = (soma, soma, soma)


#http://www.dpi.inpe.br/~carlos/Academicos/Cursos/Pdi/pdi_filtros.htm
class Moda(Filtros):

    def moda(self):
        """
        Aplica filtros de passa_alta
        """

        # Limita a aplicação da técnica para pontos que possuem vizinhos.
        # qtd_linhas_espaco = len(self.matriz_filtro) - 2
        qtd_linhas_espaco = 2
        x_final=self.imagem.imagem.width - qtd_linhas_espaco
        y_final=self.imagem.imagem.height - qtd_linhas_espaco

        generator = self.imagem._get_xy(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=x_final,
            y_final=y_final,
        )

        # j = (0, 1, 2)
        j = (0, 1, 2, 3, 4)
        matriz_aux = {x:{y:(0,0,0) for y in range(y_final + 1)} for x in range(x_final + 1)}

        for x, y in generator:
            pixels = []
            for i in range(0, 5):

                pixels.append(self.imagem.pixels[x-2+i, y-2][0])
                pixels.append(self.imagem.pixels[x-2+i, y-1][0])
                pixels.append(self.imagem.pixels[x-2+i, y][0])
                pixels.append(self.imagem.pixels[x-2+i, y+1][0])
                pixels.append(self.imagem.pixels[x-2+i, y+2][0])

            pixels.sort()

            incidencias = {}
            for pix in pixels:
                if pix in incidencias:
                    incidencias[pix] += 1
                else:
                    incidencias[pix] = 1

            incidencias = sorted(
                incidencias.items(),
                key=lambda x: x[1], reverse=True
            )
            pixel_moda = incidencias[0][0]
            matriz_aux[x][y] = (pixel_moda, pixel_moda, pixel_moda)


        for x in range(x_final + 1):
            matriz_aux[x][y_final] = self.imagem.pixels[x, y_final]
            matriz_aux[x][0] = self.imagem.pixels[x, 0]

        for y in range(y_final + 1):
            matriz_aux[x_final][y] = self.imagem.pixels[x_final, y]
            matriz_aux[0][y] = self.imagem.pixels[0, y]


        generator = self.imagem._get_xy(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=x_final,
            y_final=y_final,
        )

        for x, y in generator:
            self.imagem.pixels[x, y] = matriz_aux[x][y]


class Mediana(Filtros):

    matriz_filtro = [
        [-0.5, -0.5, -0.5],
        [-0.5, 4.0, -0.5],
        [-0.5, -0.5, -0.5]
    ]

    def mediana(self):
        """
        Aplica filtros de passa_alta
        """

        # Limita a aplicação da técnica para pontos que possuem vizinhos.
        # qtd_linhas_espaco = len(self.matriz_filtro) - 2
        qtd_linhas_espaco = 2

        x_final=self.imagem.imagem.width - qtd_linhas_espaco
        y_final=self.imagem.imagem.height - qtd_linhas_espaco

        generator = self.imagem._get_xy(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=x_final,
            y_final=y_final,
        )

        # j = (0, 1, 2)
        j = (0, 1, 2, 3, 4)
        matriz_aux = {x:{y:(0,0,0) for y in range(y_final + 1)} for x in range(x_final + 1)}

        for x, y in generator:
            soma = []
            for i in range(0, 5):

                soma.append(self.imagem.pixels[x-2+i, y-2][0])
                soma.append(self.imagem.pixels[x-2+i, y-1][0])
                soma.append(self.imagem.pixels[x-2+i, y][0])
                soma.append(self.imagem.pixels[x-2+i, y+1][0])
                soma.append(self.imagem.pixels[x-2+i, y+2][0])

            soma.sort()
            mediana = soma[13]
            matriz_aux[x][y] = (mediana, mediana, mediana)


        for x in range(x_final + 1):
            matriz_aux[x][y_final] = self.imagem.pixels[x, y_final]
            matriz_aux[x][0] = self.imagem.pixels[x, 0]

        for y in range(y_final + 1):
            matriz_aux[x_final][y] = self.imagem.pixels[x_final, y]
            matriz_aux[0][y] = self.imagem.pixels[0, y]


        generator = self.imagem._get_xy(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=x_final,
            y_final=y_final,
        )

        for x, y in generator:
            self.imagem.pixels[x, y] = matriz_aux[x][y]


class Robert(Filtros):

    matriz_y = [
        [1, 0, -1],
        [2, 0, -2],
        [1, 0, -1]
    ]

    # matriz_x = [
    #     [1, 0],
    #     [0, -1],
    # ]

    matriz_x = [
        [1, 2, 1],
        [0, 0, 0],
        [-1, -2, -1]
    ]

    # matriz_y = [
    #     [0, 1],
    #     [-1, 0],
    # ]

    def correlacao(self, rotacionar_matriz_180=False):
        """
        Aplica o filtro de correlação.
        """

        qtd_linhas_espaco = len(self.matriz_x) - 2

        x_final=self.imagem.imagem.width - qtd_linhas_espaco
        y_final=self.imagem.imagem.height - qtd_linhas_espaco

        generator = self.imagem._get_xy(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=self.imagem.imagem.width - qtd_linhas_espaco,
            y_final=self.imagem.imagem.height - qtd_linhas_espaco,
        )

        matriz_aux = {x:{y:(0,0,0) for y in range(y_final + 1)} for x in range(x_final + 1)}

        j = (0, 1, 2)
        # if rotacionar_matriz_180:
        #     j = (2, 1, 0)

        from IPython import embed; embed()
        for x, y in generator:
            soma = 0
            for i in range(0, 3):
                soma += self.imagem.pixels[x-1+i, y-1][0] * self.matriz_x[i][j[0]]
                soma += self.imagem.pixels[x-1+i, y][0] * self.matriz_x[i][j[1]]
                soma += self.imagem.pixels[x-1+i, y+1][0] * self.matriz_x[i][j[2]]
            matriz_aux[x][y] = (soma, soma, soma)

        for x in range(x_final + 1):
            matriz_aux[x][y_final] = self.imagem.pixels[x, y_final]
            matriz_aux[x][0] = self.imagem.pixels[x, 0]

        for y in range(y_final + 1):
            matriz_aux[x_final][y] = self.imagem.pixels[x_final, y]
            matriz_aux[0][y] = self.imagem.pixels[0, y]


        generator = self.imagem._get_yx(
            x_inicio=qtd_linhas_espaco,
            y_inicio=qtd_linhas_espaco,
            x_final=self.imagem.imagem.width - qtd_linhas_espaco,
            y_final=self.imagem.imagem.height - qtd_linhas_espaco,
        )

        j = (0, 1, 2)
        from IPython import embed; embed()
        for x, y in generator:
            soma = 0
            for i in range(0, 3):
                soma += matriz_aux[x-1+i][y-1][0] * self.matriz_y[i][j[0]]
                soma += matriz_aux[x-1+i][y][0] * self.matriz_y[i][j[1]]
                soma += matriz_aux[x-1+i][y+1][0] * self.matriz_y[i][j[2]]
            self.imagem.pixels[x, y] = (soma, soma, soma)


        # generator = self.imagem._get_xy(
        #     x_inicio=qtd_linhas_espaco,
        #     y_inicio=qtd_linhas_espaco,
        #     x_final=self.imagem.imagem.width - qtd_linhas_espaco,
        #     y_final=self.imagem.imagem.height - qtd_linhas_espaco,
        # )
        # for x, y in generator:
        #     self.imagem.pixels[x, y] =  matriz_aux[x][y]

        # generator = self.imagem._get_xy(
        #     x_inicio=qtd_linhas_espaco,
        #     y_inicio=qtd_linhas_espaco,
        #     x_final=self.imagem.imagem.width - qtd_linhas_espaco,
        #     y_final=self.imagem.imagem.height - qtd_linhas_espaco,
        # )
        # import math
        # for x, y in generator:
        #     v = int(math.sqrt(matriz_aux[x][y][0] ^ 2 + matriz_aux_2[x][y][0] ^ 2))
        #     if v > 255:
        #         v = 255
        #
        #     self.imagem.pixels[x, y] = (v, v, v)


        # len_x = len(matrix_norm)
        # max_pix = max(matrix_norm[0])
        # min_pix = min(matrix_norm[0])
        # for x in range(0, len_x):
        #     aux_max = max(matrix_norm[x])
        #     aux_min = min(matrix_norm[x])
        #     if aux_max > max_pix:
        #         max_pix = aux_max
        #     if aux_min < min_pix:
        #         min_pix = aux_min
        #
        # generator = self.imagem._get_xy(
        #     x_inicio=qtd_linhas_espaco,
        #     y_inicio=qtd_linhas_espaco,
        #     x_final=self.imagem.imagem.width - qtd_linhas_espaco,
        #     y_final=self.imagem.imagem.height - qtd_linhas_espaco,
        # )
        #
        # from IPython import embed; embed()
        # if max_pix > 255 or min_pix <0:
        #     for x, y in generator:
        #         pixel = self.imagem.pixels[x, y]
        #         aux = ( 255/(max_pix-min_pix) ) * (pixel[0]-min_pix)
        #
        #         self.imagem.pixels[x, y] = (aux, aux, aux)





    def robert_convolucao(self):
        """
        Aplica o filtro de convolução.
        """
        self.correlacao(rotacionar_matriz_180=True)
