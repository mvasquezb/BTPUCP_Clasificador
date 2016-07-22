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


def strip_punctuation(text):
    """""Elimina los signos de puntuacion del texto"""

    return re.sub('[%s]]' % re.escape(string.punctuation), ' ', text)

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
                for texto in f2.read().splitlines():
                    print(texto)
                    texto=texto.lower()
                    texto=strip_punctuation(texto)
                    for palabra in texto.split():
                        if palabra not in stopEnglish and palabra not in stopSpanish:                          
                            palabra=tagger.tag_text(palabra)[0].split()[2]
                            #Return [[word,type of word, lemma]]
                            palabra=palabra.replace("\ufeff","")
                            dicc_ofertas[categoria].add(palabra)
                            
    for cat in dicc_ofertas.keys():
        dicc_ofertas[cat]=list(dicc_ofertas[cat])
        
    with open(carrera+'/categorias.txt') as f:
        lineas = f.readlines()
        for palabra in lineas:
            palabra=palabra.replace("\n","")
            if palabra not in dicc_ofertas.keys():
                dicc_ofertas[palabra]=[]

    
    return dicc_ofertas

