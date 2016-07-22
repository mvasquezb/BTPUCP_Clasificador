from nltk.corpus import stopwords
import csv
import operator
import codecs
import string
import math
import unicodedata
import treetaggerwrapper
import openpyxl
import re
import numpy
import warnings
from nltk.stem.snowball import SpanishStemmer

from reconst_dicc import rec_dicc 

import matplotlib.pyplot as plt
from sklearn import datasets, svm, metrics
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation

from clasificador_categorias import Maximizador

class Core():
    carrera=""
    categorias=list()

    def __init__(self,carrera):
        self.carrera=carrera

    def strip_numbers(self, text):
        "Elimina los números del texto"

        return ''.join([letter for letter in text if not letter.isdigit()])

    def strip_punctuation(self,text):
        "Elimina los signos de puntuacion del texto"

        return re.sub('[%s]]' % re.escape(string.punctuation),' ',text)

    def obtenerDataEtiquetada(self,carrera):
        "Lee de un archivo la etiqueta que le corresponde a cada oferta."
        
        dataEtiquetada={}
        Id=0
        categoria=1
        with open(carrera+'/dataEtiquetadaABCD.txt','r') as f:
        #with open(carrera+'/dataEtiquetada.txt','r') as f:
            ofertas=csv.reader(f)
            for oferta in ofertas:
                dataEtiquetada[int(oferta[Id])]=oferta[categoria].lower()            
        return dataEtiquetada


    def obtenerDataset(self,dataEtiquetada,carrera):
        "Lee las ofertas desde el archivo ofertasCSV.txt y las inserta en una lista."
        
        Id=0
        dataset=[]
        with open(carrera+'/dataEntrenamiento.txt','r') as f:
        #with open('ofertasCSV_completo.txt') as f:
            ofertas = csv.reader(f)
            for oferta in ofertas:
                if int(oferta[Id]) in dataEtiquetada.keys():
                    dataset.append(oferta)
        return self.limpiarDataset(dataset)


    def limpiarDataset(self,dataset):
        """Quita los signos de puntuación, pasa todo a minúsculas,
        quita los números, elimina los stopwords(inglés y español)
        y pasa todas las palabras a forma raíz."""
        
        lemmatizador=treetaggerwrapper.TreeTagger(TAGLANG='es')    
        for oferta in dataset:
            for atributo in range(1,len(oferta)):
                oferta[atributo] = oferta[atributo].lower()            
                oferta[atributo] = self.strip_punctuation(oferta[atributo])
                oferta[atributo] = self.strip_numbers(oferta[atributo])

        stopEnglish = stopwords.words('english')
        stopSpanish = stopwords.words('spanish')    
        stopSpanish.append('y/o')
        Id=0
        firstElement=0
        for oferta in dataset:
            oferta[Id]=oferta[Id].replace("\ufeff","")
            numAtributos=len(oferta)
            for atributo in range(1,numAtributos):            
                cadena=""
                for word in oferta[atributo].split():
                    if word not in stopEnglish and word not in stopSpanish:
                        word=word.replace("\ufeff","")
                        lemmaResult=lemmatizador.tag_text(word)
                        #Return [[word,type of word, lemma]]
                        if(len(lemmaResult)!=0):
                            word=lemmaResult[firstElement].split()[2]                    
                            cadena+=word+" "                    
                oferta[atributo]=cadena
        
        return dataset        



    def fill_TF_IDF(self,dataset,diccionario,categorias):
        """Se llena un diccionario con 0's para luego llenarlos al momento de
        hacer el tf-idf"""
        
        TF_IDF={}

        Id=0
        for oferta in dataset:
            TF_IDF[int(oferta[Id])]={}  
        
        
        for ID in TF_IDF.keys():
            for cat in categorias:
                TF_IDF[ID][cat]=[]
                if(len(diccionario[cat])==0):
                    TF_IDF[ID][cat]=[0]
                    print("No hay palabras de la categoria " + cat)
                else:
                    TF_IDF[ID][cat]=[0]*len(diccionario[cat])                            

        return TF_IDF


    def calcular_idf(self,dataset,diccionario):
        """ Se calcula el idf de cada palabra por diccionario. Se sigue la fórmula idf = log(N/DF)
        N siendo la cantidad de avisos."""

        N=len(dataset)
        idf={}
        titulo=1
        descripcion=2
        requerimientos=3
        for cat in diccionario.keys():
            for palabra in diccionario[cat]:
                DF=int(0)
                for oferta in dataset:
                    if((palabra in oferta[titulo])or (palabra in oferta[descripcion]) or (palabra in oferta[requerimientos])):
                        DF+=1
                if(DF==0):
                    idf[palabra]=0
                else:
                    idf[palabra]=math.log(N/DF)

        return idf


    def normalizacion(self,dataset,diccionario,TF_IDF,idf):
        """Se normalizan los valores de TF_IDF dividiendo cada valor entre la
        palabra con la mayor frecuencia de la oferta."""
        
        max_frec={}
        indID=0
        titulo=1
        descripcion=2
        requerimientos=3
        for oferta in dataset:
            Id=int(oferta[indID])
            max_frec[Id]={}
            for cat in diccionario.keys():
                maximo=0 #se guarda el maximo, para hacer la normalizacion luego del calculo del tf-idf
                for palabra in diccionario[cat]:
                    tf = oferta[titulo].count(palabra)
                    tf+=oferta[descripcion].count(palabra)
                    tf+=oferta[requerimientos].count(palabra)
                    if tf > maximo:
                        maximo=tf
                    TF_IDF[Id][cat][diccionario[cat].index(palabra)]=int(tf)*idf[palabra]
                        #se agrega la cantidad en la posición correspondiente
                max_frec[Id][cat]=maximo

        for Id in TF_IDF.keys():
            for cat in diccionario.keys():
                for indWord in range(len(TF_IDF[Id][cat])):
                    if max_frec[Id][cat]>0:
                        TF_IDF[Id][cat][indWord]/=max_frec[Id][cat]
        return TF_IDF


    def calcularTF_IDF(self,diccionario,dataset,categorias ):
        "Calcula el tf-idf para el dataset que se usará para las pruebas."
        #print(len(dataset))
        #comienza inicializacion de la estructura para calcular tf-idf
        TF_IDF=self.fill_TF_IDF(dataset,diccionario,categorias)

        idf=self.calcular_idf(dataset,diccionario)

        TF_IDF=self.normalizacion(dataset,diccionario,TF_IDF,idf)
                        
        #print(len(TF_IDF))
        return TF_IDF    
        

    def obtenerCategorias(self,carrera):
        "Obtiene las categorías que pertenecen a la carrera escogida."
        
        categorias=[]

        with open(carrera+'/categorias.txt') as f:
        #with open(carrera+'/categorias.txt') as f:
            lineas=f.readlines()        
            for categoria in lineas:
                categoria=categoria.lower()
                categorias.append(categoria.replace("\n",""))
        categorias.sort()
        return categorias
                

    def obtenerData(self,TF_IDF,categorias):
        data=[]
        for Id in sorted(TF_IDF.keys()):
            oferta=[]
            for categoria in categorias:
                categoriasXoferta=[]
                for frec in TF_IDF[Id][categoria]:
                    categoriasXoferta.append(frec)
                oferta.append(categoriasXoferta)
            data.append(oferta)
        return data
            

    def mostrarResultados(self,clasificador,expected,predicted):
        """Muestra la los resultados de precision, recall y f1-score para cada
           categoría y el promedio de estas. También muestra la matriz de confusión.
    """
        reporte="Classification report for classifier %s:\n%s\n"% (clasificador, metrics.classification_report(expected, predicted))
        matriz_confusion="Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted)
        return reporte,matriz_confusion


    def entrenamiento(self,TF_IDF,dataEtiquetada,categorias):
        """Esta función entre a los clasificadores dentro del maximizador
           y prueba los datos usando cross validation."""
        
        data=[]
        expected=[]
        for Id in sorted(TF_IDF.keys()):
            oferta=[]
            for categoria in categorias:
                categoriasXoferta=[]
                for frec in TF_IDF[Id][categoria]:
                    categoriasXoferta.append(frec)
                oferta.append(categoriasXoferta)
            data.append(oferta)
            expected.append(dataEtiquetada[Id])
        
        clasificador=Maximizador(0,"defaultValue",categorias)

        #data contiene [[[],[],[],...,[]],[[],[],[],...,[]],...,[[],[],[],...,[]]]
        #Siendo el primer indice, la oferta, el segundo indice la categoria, y el tercer indice el TF_IDF
        predicted=cross_validation.cross_val_predict(clasificador,data,expected,cv=10)
        
        reporte,matriz_confusion=self.mostrarResultados(clasificador,expected,predicted)

        return clasificador,reporte,matriz_confusion        


    def predecir(self,clasificador, ofertas,carrera):        

        diccionario = rec_dicc(carrera)
        categorias=self.obtenerCategorias(self.carrera)
        self.categorias=categorias
        TF_IDF=self.calcularTF_IDF(diccionario,ofertas,categorias)  
        
        data=self.obtenerData(TF_IDF,categorias)
        predicted,matrizConocimientos,matrizSimilitudes=clasificador.predecir(data)
        return predicted,matrizConocimientos,matrizSimilitudes  


    def obtenerDatasetClas(self,filename):
        "Se lee un archivo Excel con las ofertas a clasificar"

        dataset=[]
        wb=openpyxl.load_workbook(filename)
        sheets=wb.get_sheet_names()
        sheetAviso=wb.get_sheet_by_name(sheets[0])
        maxFilas=sheetAviso.max_row+1
        maxColumnas=sheetAviso.max_column+1
        for num_oferta in range(2,maxFilas):
            fila=[]
            for nColumna in range(1,maxColumnas):
                fila.append(str(sheetAviso.cell(row=num_oferta,column=nColumna).value))
            dataset.append(fila)

        return self.limpiarDataset(dataset)


    def EjecutarEntrenamiento(self):
        dataEtiquetada=self.obtenerDataEtiquetada(self.carrera)
        dataset=self.obtenerDataset(dataEtiquetada,self.carrera)
        diccionario=rec_dicc(self.carrera)
        categorias=self.obtenerCategorias(self.carrera)
        TF_IDF=self.calcularTF_IDF(diccionario,dataset,categorias)
        clasificador,res1,res2=self.entrenamiento(TF_IDF,dataEtiquetada,categorias)
        return res1,res2
        

    def EjecutarClasificacion(self,filename):
        dataEtiquetada=self.obtenerDataEtiquetada(self.carrera)
        dataset=self.obtenerDataset(dataEtiquetada,self.carrera)
        diccionario=rec_dicc(self.carrera)
        categorias=self.obtenerCategorias(self.carrera)
        TF_IDF=self.calcularTF_IDF(diccionario,dataset,categorias)
        clasificador,res1,res2=self.entrenamiento(TF_IDF,dataEtiquetada,categorias)
        print("termino entrenamiento")
        datasetClas=self.obtenerDatasetClas(filename)
        predicted,mat_con,mat_sim=self.predecir(clasificador,datasetClas,self.carrera)        
        self.imprimir(datasetClas,predicted)
        return mat_con,mat_sim

    def imprimir(self,datasetClas,predicted):
        with open(self.carrera+"/DataClasificada_2014_BTPUCP.txt",'w') as f:
            for i in range(len(datasetClas)):
                f.write("%s: %s\n"%(datasetClas[i][0],predicted[i]))
