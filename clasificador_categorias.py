from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn import datasets, svm, metrics
from sklearn import cross_validation
import numpy

from sklearn.naive_bayes import BernoulliNB
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier

class Maximizador(BaseEstimator, ClassifierMixin):
    categorias=[]
    clasificadores={}
    umbrales={}
    probabilidadesXcategoria = {}

    def __init__(self, intValue=0, stringParam="defaultValue",categorias=list()):
        self.intValue=intValue
        self.stringParam=stringParam

        self.categorias=categorias
        for categoria in self.categorias:
            self.clasificadores[categoria]=BernoulliNB()
            self.probabilidadesXcategoria[categoria] = set()
            #self.clasificadores[categoria]=svm.SVC(probability=True)
            #self.clasificadores[categoria]=LogisticRegression(C=1.0,penalty='l2',solver='liblinear',multi_class='ovr',n_jobs=3)

             
    def obtenerEtiquetas(self,dataEtiquetada,nomb_categoria):
        etiquetas=[]
        for cat in dataEtiquetada:
            if cat==nomb_categoria:
                etiquetas.append(cat)
            else:
                etiquetas.append("null")
        return etiquetas

    def create_dataXcategoria(self,data):
        dataXcategoria={}
        for categoria in self.categorias:
            dataXcategoria[categoria]=[]

        #data contiene [[[],[],[],...,[]],[[],[],[],...,[]],...,[[],[],[],...,[]]]
        #Siendo el primer indice, la oferta, el segundo indice, la categoria, y el tercer indice el TF_IDF
        for oferta in data:
            for indCategoria in range(len(self.categorias)):
                dataXcategoria[self.categorias[indCategoria]].append(oferta[indCategoria])

        return dataXcategoria

    def fit(self,data,etiquetas=None):
        dataXcategoria=self.create_dataXcategoria(data)

        for categoria in self.categorias:
            dataPreprocesada=self.obtenerEtiquetas(etiquetas,categoria)
            self.clasificadores[categoria].fit(dataXcategoria[categoria],dataPreprocesada)
        
        return self

    def fill_predicted(self,dataXcategoria):
        predicted={}
        for categoria in self.categorias:
            predicted[categoria]=self.clasificadores[categoria].predict_proba(dataXcategoria[categoria])
            #print(self.clasificadores[categoria].classes_)  #permite saber el orden de las clases en el predict_proba
        return predicted


    def clasificarData(self,data,predicted):
        dataClasificada=[]
        for oferta in range(len(data)):
            probabilidades=list()
            for categoria in self.categorias:
                if(categoria<"null"):
                    indice_probabilidad=0
                else:
                    indice_probabilidad=1
                probabilidades.append(predicted[categoria][oferta][indice_probabilidad])

            for indProbabilidad in range(len(probabilidades)):
                tupla = (oferta,probabilidades[indProbabilidad])
                self.probabilidadesXcategoria[self.categorias[indProbabilidad]].add(tupla)

            categoria_escogida=probabilidades.index(max(probabilidades))                
            dataClasificada.append(self.categorias[categoria_escogida])
        return dataClasificada


    def clasificarData_Matriz(self,data,predicted):

        version_1=False

        matriz_conocimientos=[[0 for x in range(len(self.categorias))] for x in range(len(self.categorias))]
        matriz_similitud = [[{} for x in range(len(self.categorias))] for x in range(len(self.categorias))]

        for i in range(len(self.categorias)):
            for j in range(len(self.categorias)):
                matriz_similitud[i][j]['Alto']=0
                matriz_similitud[i][j]['Medio']=0
                matriz_similitud[i][j]['Bajo']=0

        dataClasificada=[]
        for oferta in range(len(data)):
            probabilidades=list()
            for categoria in self.categorias:
                if(categoria<"null"):
                    indice_probabilidad=0
                else:
                    indice_probabilidad=1
                probabilidades.append(predicted[categoria][oferta][indice_probabilidad])
            indEtiqueta=probabilidades.index(max(probabilidades))                
            dataClasificada.append(self.categorias[indEtiqueta])

            if version_1:
                umbralMayor,umbralMenor=self.calcularUmbrales(max(probabilidades))
                for indCategoria in range(len(self.categorias)):
                    if(indEtiqueta!=indCategoria):
                        probability=probabilidades[indCategoria]
                        if (probability>=umbralMayor):
                            nombreGrupo="Alto"
                            matriz_conocimientos[indEtiqueta][indCategoria]+=1
                            print("Numero Categoria: ",oferta,"Categoria Etiquetada: ",self.categorias[indEtiqueta],"Categoria que pasa umbral: ",self.categorias[indCategoria])
                        elif (probability>=umbralMenor):
                            nombreGrupo="Medio"
                            matriz_conocimientos[indEtiqueta][indCategoria]+=1
                            print("Numero Categoria: ", oferta, "Categoria Etiquetada: ", self.categorias[indEtiqueta],
                                  "Categoria que pasa umbral: ", self.categorias[indCategoria])
                        else:
                            nombreGrupo="Bajo"
                        matriz_similitud[indEtiqueta][indCategoria][nombreGrupo]+=1
                    else:
                        matriz_conocimientos[indEtiqueta][indCategoria]+=1
            else:
                for indCategoria in range(len(self.categorias)):
                    if (indEtiqueta != indCategoria):
                        probability = probabilidades[indCategoria]
                        if(probability>=self.umbrales[self.categorias[indCategoria]]):
                            matriz_conocimientos[indEtiqueta][indCategoria] += 1
                            print("Numero Categoria: ", oferta, "Categoria Etiquetada: ", self.categorias[indEtiqueta],
                                  "Categoria que pasa umbral: ", self.categorias[indCategoria])
                    else:
                        matriz_conocimientos[indEtiqueta][indCategoria] += 1

        return dataClasificada,matriz_conocimientos,matriz_similitud

    def calcularUmbrales(self,prob_mayor):
        umbralMayor=prob_mayor*2/3
        umbralMenor=prob_mayor/3
        return umbralMayor,umbralMenor

    def calcularUmbrales_V2(self):
        indProb = 1
        for categoria in self.categorias:
            probabilidades = []
            for tupla in self.probabilidadesXcategoria[categoria]:
                probabilidades.append(tupla[indProb])
            # SE CALCULA MEDIANA
            self.umbrales[categoria] = numpy.median(probabilidades)

    def predict(self,data,y=None):
    
        dataXcategoria=self.create_dataXcategoria(data)
        predicted=self.fill_predicted(dataXcategoria)
        dataClasificada=self.clasificarData(data,predicted)
        self.calcularUmbrales_V2()
        return dataClasificada

    def predecir(self,data,y=None):
    
        dataXcategoria=self.create_dataXcategoria(data)
        predicted=self.fill_predicted(dataXcategoria)
        dataClasificada,matrizConocimientos,matrizSimilitudes=self.clasificarData_Matriz(data,predicted)
        return dataClasificada,matrizConocimientos,matrizSimilitudes
