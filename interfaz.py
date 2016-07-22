import tkinter
from tkinter import *
from tkinter import tix
from tkinter import ttk
from core import Core
from extractor_dicc import leerArch

import os

global carrera
global indice
global dirA
global dirB


nucleo=None

#carreras=["Ingeniería Informática","Matemática","Física","Ingeniería Electrónica"]

def obtenerCarrera2(arg):
    global indice
    global carrera
    #global carreras
    indice=int(combo2.current())
        
    carrera=carreras[indice]
    
 
def obtenerCarrera3(arg):
    global indice
    global carrera
    #global carreras
    
    indice=int(combo3.current())
    
    carrera=carreras[indice]

def crearCarpeta():
    
    global entry
    global carrera
    global lbl
    global combo2
    global combo3
    carrera=entry.get()

    directory="D:/Users/a20121129/Desktop/VERSION SIN ID/Version clase/"+carrera
    if not os.path.exists(directory):
        os.makedirs(directory)        
        carreras.append(carrera)
        combo2.config(values=carreras)
        combo3.config(values=carreras)
        with open("Carreras.txt",'a') as f:
            f.write(carrera+"\n")
        lbl.config(text="Carpeta creada")
    else:
        lbl.config(text="Carpeta ya existe")
    

def cargarArchA():
    global dirA
    global lblDirA
    dirA=""
    dirA=tkinter.filedialog.askopenfilename(filetypes=(("Archivos txt","*.txt"),("All files","*.*")))
    if (dirA!=""):
        direccion=dirA[dirA.rindex("/")+1:] #obtiene el nombre de del archivo
        lblDirA.config(text=direccion)        

def cargarArchB():
    global dirB
    global lblDirB
    dirB=""
    dirB=tkinter.filedialog.askopenfilename(filetypes=(("Archivos txt","*.txt"),("All files","*.*")))
    if(dirB!=""):
        direccion=dirB[dirB.rindex("/")+1:]
        lblDirB.config(text=direccion)

    

def crearDicc():
    global dirA
    global dirB
    global entry

    #carrera = entry.get()
    #print(carrera)
    if not(dirA=="" or dirB=="" ):
        carrera = entry.get().replace("\n","")
        #ejecutar creacion de diccionario
        leerArch(carrera,dirA,dirB)

def llenarTab1(tab1):
    global combo1
    global entry    
    
    content=StringVar()
    entry=Entry(tab1,textvariable=content)
    entry.place(x=80,y=20)
        
    lblCarrera=Label(tab1,text="Carrera:")
    lblCarrera.place(x=20,y=20)

    '''lblOferta=Label(tab1,text="Oferta:")
    lblOferta.place(x=20,y=70)'''
    
    btnCrearCarpeta=Button(tab1,text="Crear Carpeta",command=crearCarpeta)
    btnCrearCarpeta.place(x=20,y=70)

    global lbl
    lbl=Label(tab1)
    lbl.place(x=120,y=70)
    
    lblArchA=Label(tab1,text="Archivo A:")
    lblArchA.place(x=20,y=120)

    btnCargarA=Button(tab1,text="Cargar archivo A",command=cargarArchA)
    btnCargarA.place(x=100,y=120)

    global lblDirA
    lblDirA=Label(tab1)
    lblDirA.place(x=210,y=120)

    lblArchB=Label(tab1,text="Archivo B:")
    lblArchB.place(x=20,y=160)

    btnCargarB=Button(tab1,text="Cargar archivo B",command=cargarArchB)
    btnCargarB.place(x=100,y=160)

    global lblDirB
    lblDirB=Label(tab1)
    lblDirB.place(x=210,y=160)

    btnAceptar=Button(tab1,text="Crear Diccionario",command=crearDicc)
    btnAceptar.place(x=20,y=200)
    

    '''xscrollbar=Scrollbar(tab1,orient=HORIZONTAL)
    xscrollbar.pack(side=BOTTOM,fill=X)'''
    
def dar_formato(mat_con):
    aux1=""

    global categorias
    for i in mat_con:
        cad=""
        for j in i:
            cad+="%5d\t"%j
        aux1+=cad+"\n"

    return aux1

def clasificar(tab3,nomArch):
    nucleo=Core(carrera)
    global categorias
    
    mat_con=nucleo.EjecutarClasificacion(nomArch)
    categorias=nucleo.categorias

    #print(categorias)
    
    mat_con=dar_formato(mat_con)
    
    lblResultados=Label(tab3,text=str(mat_con))
    lblResultados.config(background="white")
    lblResultados.place(x=20,y=160)

    

def entrenar(tab2):
    nucleo=Core(carrera)
    resultados,matriz_conf=nucleo.EjecutarEntrenamiento()

    resultados="Cuadro de resultados:\n"+resultados[resultados.find("precision"):]
    
    #se muestran P,R,F y la tabla de confusión
    lblMatriz_conf=Label(tab2,text=matriz_conf)
    lblMatriz_conf.config(background="white")
    #lblMatriz_conf.place(x=20,y=160+lblResultados.winfo_width())
    lblMatriz_conf.pack(side=BOTTOM,anchor=W)
    #lblMatriz_conf.grid(row=5,column=1)
    
    lblResultados=Label(tab2,text=resultados)
    lblResultados.config(background="white")
    #lblResultados.place(x=20,y=160)
    lblResultados.pack(side=BOTTOM,anchor=W)
    #lblResultados.grid(row=6,column=1)
    

def llenarTab2(tab2):
    global combo2
    #global carreras
    combo2=ttk.Combobox(tab2,values=carreras)
    combo2.state(['readonly'])
    combo2.bind('<<ComboboxSelected>>',obtenerCarrera2)
    combo2.place(x=80,y=20)
    
    lblCarrera=Label(tab2,text="Carreras:")
    lblCarrera.place(x=20,y=20)
        
    btnAceptar=Button(tab2,text="Aceptar",command=lambda aux=1:entrenar(tab2)) 
    btnAceptar.place(x=20,y=70)
    
    

def CargarDataClasificar(tab3,btnAceptar):

    nomArch= tkinter.filedialog.askopenfilename(filetypes=(("Archivos xlsx","*.xlsx"),("All files","*.*")))

    if(nomArch!=""):
        archivo=nomArch[nomArch.rindex("/")+1:]
        lblArchivo=Label(tab3,text=archivo)
        lblArchivo.place(x=120,y=70)
        
        btnAceptar.config(command=lambda aux=1:clasificar(tab3,nomArch))

def llenarTab3(tab3):

    global combo3
    combo3=ttk.Combobox(tab3,values=carreras)

    combo3.state(['readonly'])
    combo3.bind('<<ComboboxSelected>>',obtenerCarrera3)
    combo3.place(x=80,y=20)
    
    lblCarrera=Label(tab3,text="Carreras:")
    lblCarrera.place(x=20,y=20)

    btnCargarArchivo=Button(tab3,text="Cargar Archivo",command=lambda aux=1:CargarDataClasificar(tab3,btnAceptar))
    btnCargarArchivo.place(x=20,y=70)

    btnAceptar=Button(tab3,text="Aceptar") 
    btnAceptar.place(x=20,y=120)
    
def ObtenerCarreras():
    #global carreras
    carreras=[]
    with open("Carreras.txt",'r') as f:
        for carrera in f.readlines():
            carrera=carrera.replace("\n","")
            carreras.append(carrera)
    return carreras


carreras=ObtenerCarreras()

def main():
    #global carreras
    
    
    ancho=400
    alto=400
    
    global lblDirOfertas
    global btnAceptar    
    
    principal=Tk()
    #principal.resizable(height=FALSE,width=FALSE)
    principal.title("Clasificador")    

    note=ttk.Notebook(principal)

    tab1=Frame(note,width=ancho,height=alto)
    tab1.pack()
    note.add(tab1,text="Nuevo Diccionario")

    tab2=Frame(note,width=ancho,height=alto)
    tab2.pack()
    note.add(tab2,text="Entrenamiento")

    tab3=Frame(note,width=ancho,height=alto)    
    tab3.pack()
    note.add(tab3,text="Clasificar")
    
    
    note.pack(expand=YES,fill=BOTH)

    #yscrollbar=Scrollbar(tab3,orient=VERTICAL)
    #yscrollbar.pack(side=RIGHT,fill=Y)
    
    llenarTab1(tab1)            

    llenarTab2(tab2)

    llenarTab3(tab3)
    
    principal.mainloop()


main()
