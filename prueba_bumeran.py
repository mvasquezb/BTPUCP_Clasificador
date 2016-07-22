import csv

def prueba():
    with open("bumeran_2015_2_informatica.txt",'r',-1,'utf-8') as f:
        a=set()
        ofertas=csv.reader(f)
        for oferta in ofertas:
            a.add(int(oferta[0]))
        print(len(a))
prueba()
