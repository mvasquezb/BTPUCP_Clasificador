from nltk.corpus import stopwords
import csv
import operator
import codecs
import string
import math
import unicodedata
import treetaggerwrapper
import re
from nltk.stem.snowball import SpanishStemmer

tipos=["verbo","sustantivo","frase"]


def _remove_punctuation(text):
    """""Elimina los signos de puntuacion del texto"""

    return re.sub('[%s]]' % re.escape(string.punctuation), ' ', text)


def _remove_numbers(text):
    "Elimina los números del texto"

    return ''.join([letter for letter in text if not letter.isdigit()])

def rec_dicc(carrera):
    tagger=treetaggerwrapper.TreeTagger(TAGLANG='es')
    dicc_ofertas = dict()
    stopEnglish = stopwords.words('english')
    stopSpanish = stopwords.words('spanish')
    stopSpanish.append("y/o")

    with open(carrera+"/diccProfeABCD/diccionarios.txt",'r',-1,'utf-8') as f1:
        for categoria in f1.read().splitlines():
            categoria=categoria.replace("\ufeff","")
            with open(carrera+"/diccProfeABCD/"+categoria,'r') as f2:
                categoria=categoria.replace(".txt","")
                if categoria not in dicc_ofertas.keys(): dicc_ofertas[categoria]=set()                

                for linea in f2.read().splitlines():
                    aux = ""
                    linea=linea.lower()
                    linea = _remove_punctuation(linea)
                    linea = _remove_numbers(linea)
                    if (len(linea.split()) > 1):
                        # print(j)
                        frase_dicc = linea.split()  # convertir el string en una lista de str
                        # print(frase_dicc)
                        frase_dicc = [x for x in frase_dicc if x not in stopSpanish]  # eliminar stopwords en la lista
                        frase_dicc = [x for x in frase_dicc if x not in stopEnglish]
                        lemmatizacion = tagger.tag_text(frase_dicc)
                        cadena_lemmatizada = ""
                        for i in range(len(lemmatizacion)):  # obtener las palabras lemmatizadas de la frase
                            cadena_lemmatizada += lemmatizacion[i].split()[2].replace("\ufeff", "")
                            if (i != len(lemmatizacion) - 1): cadena_lemmatizada += " "
                        # print((cadena_lemmatizada))
                        # cadena_lemmatizada = [x.replace("\ufeff","") for x in cadena_lemmatizada] #a veces este caracter raro aparece
                        # print(cadena_lemmatizada)
                        # cadena_lemmatizada = " ".join(cadena_lemmatizada) #convierte la lista de str en un str
                        # print(cadena_lemmatizada)
                        dicc_ofertas[categoria].add(cadena_lemmatizada)
                    else:
                        if (len(linea) < 1 or linea == " "): continue
                        if linea not in stopEnglish and linea not in stopSpanish:
                            linea = tagger.tag_text(linea)[0].split()[2]
                            print(linea)
                            linea = linea.replace("\ufeff", "")
                            # print(j)
                            dicc_ofertas[categoria].add(linea)
                            
    for cat in dicc_ofertas.keys():
        dicc_ofertas[cat]=list(dicc_ofertas[cat])
        
    with open(carrera+'/categorias.txt') as f:
        lineas = f.readlines()
        for palabra in lineas:
            palabra=palabra.replace("\n","")
            if palabra not in dicc_ofertas.keys():
                dicc_ofertas[palabra]=[]

    
    return dicc_ofertas

