from nltk.corpus import stopwords
import csv
import operator
import codecs
import string
import math
import unicodedata
import treetaggerwrapper
import numpy
import warnings
from nltk.stem.snowball import SpanishStemmer

from reconst_dicc import rec_dicc 

import matplotlib.pyplot as plt
from sklearn import datasets, svm, metrics
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation

from clasificador_categorias import Maximizador

tipos=["verbo","sustantivo","frase"]


def strip_numbers(s):
    "Elimina los números de la cadena s."
    
    strr2 = ""
    first=True
    for i in s.split():
        if(i.isnumeric()):
            pass
        else:
            if(first):
                strr2 += i
                first=False
            else:
                strr2 += " "+i
    return strr2


def obtenerDataEtiquetada(carrera):
    "Lee de un archivo la etiqueta que le corresponde a cada oferta."
    
    dataEtiquetada={}
    Id=0
    categoria=1
    with open('dataEtiquetada.txt','r') as f:
    #with open(carrera+'/dataEtiquetada.txt','r') as f:
        ofertas=csv.reader(f)
        for oferta in ofertas:
            dataEtiquetada[int(oferta[Id])]=oferta[categoria].lower()            
    return dataEtiquetada


def obtenerDataset(dataEtiquetada,carrera):
    "Lee las ofertas desde el archivo ofertasCSV.txt y las inserta en una lista."
    
    indiceId=0
    dataset=[]
    #with open(carrera+'/ofertasCSV.txt') as f:
    with open('ofertasCSV.txt') as f:
        ofertas = csv.reader(f)
        for oferta in ofertas:
            if int(oferta[indiceId]) in dataEtiquetada.keys():
                dataset.append(oferta)
    return limpiarDataset(dataset)


def limpiarDataset(dataset):
    "Quita los signos de puntiación, pasa todo a minúsculas, \nquita los números, elimina los stopwords(inglés y español) \ny pasa todas las palabras a forma raíz."
    
    tagger=treetaggerwrapper.TreeTagger(TAGLANG='es')    
    
    translate_table = dict((ord(char), ' ') for char in string.punctuation)
    for oferta in dataset:
        for atributo in range(1,4):            
            oferta[atributo] = oferta[atributo].lower()            
            oferta[atributo] = oferta[atributo].translate(translate_table)
            oferta[atributo] = strip_numbers(oferta[atributo])
            

    stopEnglish = stopwords.words('english')
    stopSpanish = stopwords.words('spanish')    
    stopSpanish.append('y/o')
    for i in dataset:
        i[0]=i[0].replace("\ufeff","")
        for k in range(1,len(i)):            
            aux=""
            for j in i[k].split():
                if j not in stopEnglish and j not in stopSpanish:
                    #print(j)
                    j=j.replace("\ufeff","")
                    #print(j)
                    j=tagger.tag_text(j)
                    if(len(j)!=0):
                        j=j[0].split()[2]                    
                        aux+=j+" "                    
            i[k]=aux
    #print("termino tagger")
    return dataset        



def fill_TF_IDF(dataset,diccionario,categorias):
    "Se llena un diccionario con 0's para luego llenarlos al momento de \nhacer el tf-idf"
    
    TF_IDF={}
    
    for i in dataset:
        #print(i[0])
        TF_IDF[int(i[0])]={}  
    
    
    for ID in TF_IDF.keys():
        for cat in categorias:
            TF_IDF[ID][cat]=[]
            if(len(diccionario[cat])==0):
                TF_IDF[ID][cat]=[0]
            else:
                TF_IDF[ID][cat]=[0]*len(diccionario[cat])                            

    return TF_IDF


def calcular_idf(dataset,diccionario):
    
    
    N=len(dataset)
    idf={}
    for cat in diccionario.keys():
        for palabra in diccionario[cat]:
                DF=int(0)
                for oferta in dataset:
                    if ((palabra in oferta[1]) or (palabra in oferta[2]) or (palabra in oferta[3])):
                        DF+=1
                if(DF==0):
                    #print(palabra)
                    idf[palabra]=0
                if(DF!=0):
                    idf[palabra]=math.log(N/DF)

    return idf


def normalizacion(dataset,diccionario,TF_IDF,idf):
    "Se normalizan los valores de TF_IDF dividiendo cada valor entre la \npalabra con la mayor frecuencia de la oferta."
    
    max_frec={}
    
    for oferta in dataset:
        max_frec[int(oferta[0])]={}
        for cat in diccionario.keys():
            maximo=0
            for palabra in diccionario[cat]:
                cont = oferta[1].count(palabra) #se busca en el titulo
                cont+=oferta[2].count(palabra)  #se busca en la descripcion
                cont+=oferta[3].count(palabra)  #se buscar en los requerimientos
                if cont > maximo:
                    maximo=cont
                TF_IDF[int(oferta[0])][cat][diccionario[cat].index(palabra)]=int(cont)*idf[palabra]
                    #se agrega la cantidad en la posición correspondiente
            max_frec[int(oferta[0])][cat]=maximo

    for Id in TF_IDF.keys():
        for cat in diccionario.keys():
            for frec in TF_IDF[Id][cat]:
                if max_frec[Id][cat]>0:
                    frec=frec/max_frec[Id][cat]
    return TF_IDF


def calcularTF_IDF(diccionario,dataset,categorias ):
    "Calcula el tf-idf para el dataset que se usará para las pruebas."
    
    #comienza inicializacion de la estructura para calcular tf-idf
    TF_IDF=fill_TF_IDF(dataset,diccionario,categorias)

    idf=calcular_idf(dataset,diccionario)

    TF_IDF=normalizacion(dataset,diccionario,TF_IDF,idf)
                    
    
    return TF_IDF

    
def main(args):
    "Recibe como parametro una lista con la carrera a analizar y la ruta del\narchivo con las ofertas que se quiere clasificar."
    
    carrera=args[1]
    
    dataEtiquetada=obtenerDataEtiquetada(carrera)    
            
    dataset=obtenerDataset(dataEtiquetada,carrera)    

    diccionario = rec_dicc() #se recupera el diccionario de los datos etiquetados
    
    categorias=obtenerCategorias(carrera)

    TF_IDF=calcularTF_IDF(diccionario,dataset,categorias)
    
    clasificador=entrenamiento(TF_IDF,dataEtiquetada,categorias)

    #a partir de aquí recién se pueden hacer predicciones de nuevas ofertas, faltan esas funciones

    datasetClas=obtenerDatasetClas('ofertaCSV_2015.txt')
    predicted,TF_IDF_clas=predecir(clasificador,datasetClas,carrera)
    #matriz=clasificador.crearMatriz(predicted,TF_IDF_clas)
    #print(matriz)
    

def obtenerCategorias(carrera):
    "Obtiene las categorías que pertenecen a la carrera escogida."
    
    categorias=[]

    with open('categorias.txt') as f:
    #with open(carrera+'/categorias.txt') as f:
        lineas=f.readlines()        
        for i in lineas:
            i=i.lower()
            categorias.append(i.replace("\n",""))
    categorias.sort()
    return categorias
            

def obtenerData(TF_IDF,categorias):
    data=[]
    for Id in sorted(TF_IDF.keys()):
        oferta=[]
        for categoria in categorias:
            #lst=[Id]
            lst=[]
            for frec in TF_IDF[Id][categoria]:
                lst.append(frec)
            oferta.append(lst)
        data.append(oferta)
    return data
        

def mostrarResultados(clasificador,expected,predicted):
    print("Classification report for classifier %s:\n%s\n"
      % (clasificador, metrics.classification_report(expected, predicted)))
    print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))


def entrenamiento(TF_IDF,dataEtiquetada,categorias):
    "Esta función entre a los clasificadores dentro del maximizador\ny prueba los datos usando cross validation."    
    
    data=[]
    expected=[]
    for Id in sorted(TF_IDF.keys()):
        oferta=[]
        for categoria in categorias:
            #lst=[Id]
            lst=[]
            for frec in TF_IDF[Id][categoria]:
                lst.append(frec)
            oferta.append(lst)
        data.append(oferta)
        expected.append(dataEtiquetada[Id])
    
    clasificador=Maximizador(0,"defaultValue",categorias)
    
    predicted=cross_validation.cross_val_predict(clasificador,data,expected,cv=10)

    
    mostrarResultados(clasificador,expected,predicted)

    

    return clasificador        


def predecir(clasificador, ofertas,carrera):        

    diccionario = rec_dicc()
    categorias=obtenerCategorias(carrera)
    TF_IDF=calcularTF_IDF(diccionario,ofertas,categorias)  
    
    data=obtenerData(TF_IDF,categorias)
    predicted,matrizConocimientos,matrizSimilitudes=clasificador.predecir(data)
    print(matrizConocimientos)
    print(matrizSimilitudes)
    return predicted,TF_IDF  


def obtenerDatasetClas(filename):
    dataset=[]
    with open(filename,'r',-1,'utf-8')as f:
        ofertas = csv.reader(f)
        for oferta in ofertas:
            
            dataset.append(oferta)
    return limpiarDataset(dataset)


    
with warnings.catch_warnings():
    warnings.simplefilter("ignore")    
    main(["","Ingeniería Informática"])
