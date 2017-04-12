import csv
import codecs
import string
import math
import unicodedata

#tipos = ["frase","verbo","sustantivo"]



def guardar_dicc(carrera,dicc_ofertas):
    with open(carrera+'/diccProfeABCD/diccionarios.txt','w',-1,'utf-8')as f:
        for categoria in dicc_ofertas:            
            f.write(categoria+".txt\n")

    for categoria in dicc_ofertas:        
        with open(carrera+'/diccProfeABCD/'+categoria+'.txt','w',-1,'utf-8') as f:
            for elem in dicc_ofertas[categoria]:
                f.write(elem)
                f.write("\n")
    #print("termino de escribir")

def crear_dicc(dataset):
    dicc_ofertas = dict()
    for oferta in dataset: 
        if oferta[1] not in dicc_ofertas: dicc_ofertas[oferta[1]]=list()
        categoria = oferta[1] #indica area de carrera
        for texto in range(2,5):
            if oferta[texto]=="" or oferta[texto]=="   ":
                continue
            else:
                cad = oferta[texto]
                index=-1 
                #tipo="" #indica si es frase, verbo o sustantivo
                for palabra in cad.split():                  
                    if palabra=="frase" or palabra=="sustantivo" or palabra=="verbo":                                            
                        continue
                    if palabra[0]=="-": #primera letra de la palabra
                        dicc_ofertas[categoria].append(palabra.replace("-",""))
                        #index=len(dicc_ofertas[categoria][tipo])-1
                        #continue
                    else:
                        #dicc_ofertas[categoria][tipo][index]+=" "
                        dicc_ofertas[categoria].append(palabra)
                        #print(dicc_ofertas[categoria][tipo][index]+"\n")
                            
                        
    #eliminando posibles valores repetidos de frases, verbos y sustantivos
    for categoria in dicc_ofertas.keys():
        dicc_ofertas[categoria]=list(set(dicc_ofertas[categoria]))        

    guardar_dicc(carrera,dicc_ofertas)
    
    
def leerArch(carrera,nombArch1,nombArch2):
    dataset1=[]
    with open(nombArch1, 'r',-1,'utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            dataset1.append(row)    
    #print(len(dataset1))
    
    dataset2=[]
    with open(nombArch2, 'r',-1,'utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            dataset2.append(row)    
    #print(len(dataset2))
    
    dataset=elimin_vacios(carrera,dataset1,dataset2)
    dicc_ofertas = crear_dicc(carrera,dataset)
    #return dicc_ofertas


def leerFilas(nombArch):
    
    lista=[]
    arch=open(nombArch,'r')
    for linea in arch.readlines():
        num=int(linea)
        lista.append(num)

    arch.close()
    return lista

def elimin_vacios(carrera,dataset1,dataset2):

    dataset=[]
    listaRechazados=leerFilas('diferencias_informatica.txt')
    dataAnotada=[]
    #dataset1.sort()
    #dataset2.sort()
    for numOferta in range(len(dataset1)):
        filaDS1=dataset1[numOferta]
        filaDS2=dataset2[numOferta]
        if not(filaDS1[1]==' ' or filaDS2[1]==' ' or int(filaDS1[0]) in listaRechazados):
            print(filaDS1[1] + " ID: "+filaDS1[0])
            par=[filaDS1[0],filaDS1[1]]
            dataAnotada.append(par)
            fila=[]
            fila.append(filaDS1[0])
            fila.append(filaDS1[1])

            for columna in range(2,6):
                aux=""
                aux+=filaDS1[columna]
                aux+=" "
                aux+=filaDS2[columna]
                fila.append(aux)
            dataset.append(fila)
    #print("Termino de unir")
    
    for oferta in dataset:
        for columna in range(1,6):
            oferta[columna] = oferta[columna].lower()
            #a veces ocurren errores cuando se ponen
            #enter en el excel, por eso reemplazo
            oferta[columna]=oferta[columna].replace("-verbo","verbo")
            oferta[columna]=oferta[columna].replace("-sustantivo","sustantivo")
            oferta[columna]=oferta[columna].replace("-frase","frase")
            #en algunos casos hay un espacio luego del cambio de linea
            oferta[columna]=oferta[columna].replace("- ","-")
            

    with open(carrera+'/dataEtiquetadaABCD.txt','w') as f:
        for par in dataAnotada:
            f.write(par[0]+","+par[1]+"\n")        
            
    return dataset
            


#dicc_ofertas = leerArch("datosAB.txt","datosCD.txt")
