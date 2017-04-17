#!/usr/bin/env python3
import re
import math
import sys

from sklearn import metrics
from sklearn import model_selection

from clasificador_categorias import Maximizador
from input_output_text import Input_Output


class Core():
    carrera = ""
    categorias = list()
    io = None

    def __init__(self, carrera):
        self.carrera = carrera
        self.io = Input_Output()

    def _count_word(self, text, search):
        '''Esta funcion cuenta de manera exacta la palabra en el texto
        sin embargo, se cae cuando busca la palabra "++" como en "c++" '''

        result = re.findall('\\b' + search + '\\b', text, flags=re.IGNORECASE)
        return len(result)

    def fill_TF_IDF(self, dataset, diccionario, categorias):
        """Se llena un diccionario con 0's para luego llenarlos al momento de
        hacer el tf-idf"""

        TF_IDF = {}

        Id = 0
        for oferta in dataset:
            TF_IDF[int(oferta[Id])] = {}

        for ID in TF_IDF.keys():
            for cat in categorias:
                TF_IDF[ID][cat] = []
                if(len(diccionario[cat]) == 0):
                    TF_IDF[ID][cat] = [0]
                    print("No hay palabras de la categoria " + cat)
                else:
                    TF_IDF[ID][cat] = [0] * len(diccionario[cat])

        return TF_IDF

    def calcular_idf(self, dataset, diccionario):
        """
        Se calcula el idf de cada palabra por diccionario.
        Se sigue la fórmula idf = log(N/DF)
        N siendo la cantidad de avisos.
        """

        N = len(dataset)
        idf = {}
        titulo = 1
        descripcion = 2
        requerimientos = 3
        for cat in diccionario.keys():
            for palabra in diccionario[cat]:
                DF = int(0)
                for oferta in dataset:
                    if((palabra in oferta[titulo]) or
                       (palabra in oferta[descripcion]) or
                       (palabra in oferta[requerimientos])):
                        DF += 1
                if(DF == 0):
                    idf[palabra] = 0
                else:
                    idf[palabra] = math.log(N / DF)

        return idf

    def normalizacion(self, dataset, diccionario, TF_IDF, idf):
        """Se normalizan los valores de TF_IDF dividiendo cada valor entre la
        palabra con la mayor frecuencia de la oferta."""

        max_frec = {}
        indID = 0
        titulo = 1
        descripcion = 2
        requerimientos = 3
        for oferta in dataset:
            Id = int(oferta[indID])
            max_frec[Id] = {}
            for cat in diccionario.keys():
                # Se guarda el maximo, para hacer la normalizacion
                # luego del calculo del tf-idf
                maximo = 0
                for palabra in diccionario[cat]:
                    # print("Palabra:",palabra)
                    # print("Titulo:",oferta[titulo])
                    palabra = str(palabra)
                    tf = self._count_word(str(oferta[titulo]), palabra)
                    tf += self._count_word(str(oferta[descripcion]), palabra)
                    tf += self._count_word(
                        str(oferta[requerimientos]),
                        palabra
                    )
                    if tf > maximo:
                        maximo = tf
                    TF_IDF[Id][cat][
                        diccionario[cat].index(palabra)
                    ] = int(tf) * idf[palabra]
                    # se agrega la cantidad en la posición correspondiente
                max_frec[Id][cat] = maximo

        for Id in TF_IDF.keys():
            for cat in diccionario.keys():
                for indWord in range(len(TF_IDF[Id][cat])):
                    if max_frec[Id][cat] > 0:
                        TF_IDF[Id][cat][indWord] /= max_frec[Id][cat]

        return TF_IDF

    def calcularTF_IDF(self, diccionario, dataset, categorias):
        "Calcula el tf-idf para el dataset que se usará para las pruebas."
        # print(len(dataset))
        # comienza inicializacion de la estructura para calcular tf-idf
        TF_IDF = self.fill_TF_IDF(dataset, diccionario, categorias)

        idf = self.calcular_idf(dataset, diccionario)

        TF_IDF = self.normalizacion(dataset, diccionario, TF_IDF, idf)

        return TF_IDF

    def tranformarDataALista(self, TF_IDF, categorias):
        data = []
        for Id in sorted(TF_IDF.keys()):
            oferta = []
            for categoria in categorias:
                categoriasXoferta = []
                for frec in TF_IDF[Id][categoria]:
                    categoriasXoferta.append(frec)
                oferta.append(categoriasXoferta)
            data.append(oferta)
        return data

    def obtenerCategoriasEsperadas(self, TF_IDF, dataEtiquetada):
        expected = []
        for Id in sorted(TF_IDF.keys()):
            expected.append(dataEtiquetada[Id])
        return expected

    def mostrarResultados(self, clasificador, expected, predicted):
        """
        Muestra la los resultados de precision, recall y f1-score para cada
        categoría y su promedio. También muestra la matriz de confusión.
        """
        reporte = "Classification report for classifier %s:\n%s\n" % (
            clasificador, metrics.classification_report(expected, predicted))
        matriz_confusion = "Confusion matrix:\n%s" % metrics.confusion_matrix(
            expected, predicted)
        return reporte, matriz_confusion

    def entrenamiento(self, TF_IDF, dataEtiquetada, categorias):
        """Esta función entre a los clasificadores dentro del maximizador
           y prueba los datos usando cross validation."""

        data = self.tranformarDataALista(TF_IDF, categorias)
        expected = self.obtenerCategoriasEsperadas(TF_IDF, dataEtiquetada)

        clasificador = Maximizador(intValue=0, categorias=categorias)

        # data contiene [[[],[],[],...,[]],[[],[],[],...,[]],...,[[],[],[],...,[]]]
        # Siendo el primer indice, la oferta, el segundo indice la categoria, y
        # el tercer indice el TF_IDF
        predicted = model_selection.cross_val_predict(
            clasificador,
            data,
            expected,
            cv=10
        )

        reporte, confusion_matrix = self.mostrarResultados(
            clasificador, expected, predicted)

        return clasificador, reporte, confusion_matrix

    def crearMatriz(self, diccionario, categorias, predicted, ofertas):

        for categoria in categorias:
            print("Cantidad de", categoria, ":", predicted.count(categoria))

        conteo_Categorias_Palabras = {}
        for categoriaEtiqueta in categorias:
            conteo_Categorias_Palabras[categoriaEtiqueta] = {}
            for categoria in categorias:
                conteo_Categorias_Palabras[categoriaEtiqueta][categoria] = {}

        matriz_conocimientos = [
            [0 for x in range(len(categorias))]
            for x in range(len(categorias))
        ]

        titulo = 1
        descripcion = 2
        requerimientos = 3
        for numOferta in range(len(predicted)):
            categoriaEtiqueta = predicted[numOferta]
            indCategoriaEtiquetada = categorias.index(categoriaEtiqueta)

            for categoria in categorias:
                indCategoria = categorias.index(categoria)
                if categoriaEtiqueta != categoria:
                    alreadyCount = False
                else:
                    matriz_conocimientos[indCategoriaEtiquetada][
                        indCategoria] += 1
                    alreadyCount = True

                oferta = ofertas[numOferta]
                for palabra in diccionario[categoria]:
                    if (self._count_word(oferta[titulo], palabra) > 0 or
                        self._count_word(oferta[descripcion], palabra) > 0 or
                        self._count_word(oferta[requerimientos], palabra) > 0):
                        if palabra not in conteo_Categorias_Palabras[categoriaEtiqueta][categoria].keys():
                            conteo_Categorias_Palabras[
                                categoriaEtiqueta][categoria][palabra] = 1
                        else:
                            conteo_Categorias_Palabras[categoriaEtiqueta][
                                categoria][palabra] += 1
                        if(not(alreadyCount)):
                            matriz_conocimientos[indCategoriaEtiquetada][
                                indCategoria] += 1
                            alreadyCount = True

        return matriz_conocimientos, conteo_Categorias_Palabras

    def predecir(self, clasificador, ofertas, diccionario, categorias):

        TF_IDF = self.calcularTF_IDF(diccionario, ofertas, categorias)

        data = self.tranformarDataALista(TF_IDF, categorias)
        predicted = clasificador.predict(data)

        (matrizConocimientos,
         conteo_Categorias_Palabras) = self.crearMatriz(
            diccionario,
            categorias,
            predicted,
            ofertas
        )

        return predicted, matrizConocimientos, conteo_Categorias_Palabras

    def EjecutarEntrenamiento(self):
        (dataEtiquetada,
         dataset,
         diccionario,
         categorias) = self.io.obtenerUtilidades(self.carrera)

        TF_IDF = self.calcularTF_IDF(diccionario, dataset, categorias)

        (clasificador,
         res1,
         res2) = self.entrenamiento(TF_IDF, dataEtiquetada, categorias)

        # self.io.grabarClasificador(clasificador)

        return res1, res2

    def EjecutarClasificacion(self, filename):
        (dataEtiquetada,
         dataset,
         diccionario,
         categorias) = self.io.obtenerUtilidades(self.carrera)

        TF_IDF = self.calcularTF_IDF(diccionario, dataset, categorias)
        (clasificador,
         res1,
         res2) = self.entrenamiento(TF_IDF, dataEtiquetada, categorias)

        # clasificador=self.io.leerClasificador(categorias)

        print(clasificador.categorias)
        print(list(clasificador.clasificadores.keys()))

        print("Se finalizó la etapa de entrenamiento")
        unlabelled_dataset = self.io.obtenerDatasetAClasificar(filename)

        (predicted,
         mat_con,
         conteo_Categorias_Palabras) = self.predecir(
            clasificador,
            unlabelled_dataset,
            diccionario,
            categorias
        )
        self.io._imprimirPredicted(
            unlabelled_dataset,
            predicted,
            filename,
            self.carrera
        )
        self.io._imprimirDiccionarios(
            conteo_Categorias_Palabras,
            categorias,
            filename,
            self.carrera
        )
        return mat_con


def main(args=None):
    if args is None:
        args = sys.argv
    if len(args) < 3:
        print(
            """Faltan argumentos:
            {prog_name} CAREER_NAME DATA_FILENAME
            """.format(prog_name=sys.argv[0]),
            file=sys.stderr
        )
        return None
    core = Core(args[1])
    # res1,res2=core.EjecutarEntrenamiento()
    mat = core.EjecutarClasificacion(args[2])
    # print(res1)
    # print(res2)
    print(mat)


if __name__ == '__main__':
    main()
