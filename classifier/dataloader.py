import csv
import openpyxl
from textprocessor import TextProcessor
from pathlib import Path as OSPath
from utils import open_filename


class DataLoader:
    def __init__(self, root='.'):
        self.root = root
        self.textProcessor = TextProcessor()

    def clean_dataset(self, dataset, inplace=False):
        """
        Merge offer attributes and preprocess text
        """

        new_data = dataset if inplace else dataset.copy()
        for key, offer in new_data.items():
            new_data[key] = ' '.join(
                set(self.textProcessor.tokenize(' '.join(offer)))
            )

        return new_data

    def get_labelled_data(self, carrera):
        "Lee de un archivo la etiqueta que le corresponde a cada oferta."

        labelledData = {}
        Id = 0
        categoria = 1

        with open(str(OSPath(
            self.root, carrera, 'dataEtiquetadaABCD.txt')
        )) as f:
            offers = csv.reader(f)
            for offer in offers:
                labelledData[int(offer[Id])] = offer[categoria].lower()
        return labelledData

    def get_dataset(self, labelledData, carrera):
        """
        Lee las ofertas desde el archivo ofertasCSV.txt
        y las inserta en una lista.
        """

        Id = 0
        dataset = {}
        with open(str(OSPath(
            self.root, carrera, 'dataEntrenamiento.csv')
        )) as f:
            offers = csv.reader(f)
            # Skip header
            next(offers)
            for offer in offers:
                if int(offer[Id]) in labelledData.keys():
                    dataset[int(offer[Id])] = offer[1:]

        return self.clean_dataset(dataset)

    def get_categories(self, carrera):
        "Obtiene las categorías que pertenecen a la carrera escogida."

        categorias = []

        with open(str(OSPath(self.root, carrera, 'categorias.txt'))) as f:
            for categoria in f:
                categoria = categoria.lower()
                categorias.append(categoria.replace("\n", ""))
        categorias.sort()
        return categorias

    def get_dictionary(self, carrera, encoding='ISO-8859-1'):
        dicc_offers = {}

        with open(self.root + '/' + carrera + "/diccProfeABCD/diccionarios.txt",
                  encoding=encoding) as f1:
            lineas = f1.readlines()
            for categoria in lineas:
                categoria = categoria.replace("\n", "")
                print("Diccionarios-", categoria)
                with open(self.root + '/' + carrera + "/diccProfeABCD/" + categoria,
                          encoding='ISO-8859-1') as f2:
                    categoria = categoria.replace(".txt", "")
                    if categoria not in dicc_offers.keys():
                        dicc_offers[categoria] = set()

                    for linea in f2.read().splitlines():
                        linea = self.textProcessor.preprocessText(linea)
                        cadena_procesada = self.textProcessor.stemText(
                            linea)
                        dicc_offers[categoria].add(cadena_procesada)

        for cat in dicc_offers.keys():
            dicc_offers[cat] = list(dicc_offers[cat])

        return dicc_offers

    def get_data_for_career(self, career):
        # labelled_data = self.get_labelled_data(career)
        # dataset = self.get_dataset(labelled_data, career)
        # categories = self.get_categories(career)
        # dictionary = self.get_dictionary(career)

        # return labelled_data, dataset, dictionary, categories
        labelled_data = self.get_labelled_data(career)
        dataset = self.get_dataset(labelled_data, career)
        return dataset

    def printPredicted(self,
                       datasetClasificado,
                       predicted,
                       filename,
                       carrera):
        division_Carpetas = filename.split("/")
        nombArchivo_Extension = division_Carpetas[len(division_Carpetas) - 1]
        firstElement = 0
        nombArchivo = nombArchivo_Extension.split(".")[firstElement]
        indID = 0
        with open(self.root + '/' + carrera + "/DataClasificada_" +
                  nombArchivo + ".txt", 'w') as f:
            for i in range(len(datasetClasificado)):
                f.write("%s: %s\n" %
                        (datasetClasificado[i][indID], predicted[i]))

    def print_dictionaries(self,
                           cat_word_count,
                           categorias,
                           filename,
                           carrera):
        division_Carpetas = filename.split("/")
        nombArchivo_Extension = division_Carpetas[len(division_Carpetas) - 1]
        firstElement = 0
        nombArchivo = nombArchivo_Extension.split(".")[firstElement]
        for categoriaEtiqueta in categorias:
            for categoria in categorias:
                with open(self.root + '/' + carrera + "/Diccionario_" + nombArchivo + "_" +
                          categoriaEtiqueta + "_" +
                          categoria + ".txt", 'w') as f:
                    for palabra in sorted(cat_word_count[categoriaEtiqueta][categoria].keys()):
                        f.write("%s: %d\n" % (
                            palabra, cat_word_count[categoriaEtiqueta][categoria][palabra]))

    def _read_excel_dataset(self, filename):
        dataset = []

        wb = openpyxl.load_workbook(filename)
        sheets = wb.get_sheet_names()
        offer_sheet = wb.get_sheet_by_name(sheets[0])
        max_rows = offer_sheet.max_row + 1
        max_columns = offer_sheet.max_column + 1

        for offer_number in range(2, max_rows):
            row = []
            for col_number in range(1, max_columns):
                row.append(
                    str(offer_sheet.cell(
                        row=offer_number,
                        column=col_number
                    ).value)
                )
            dataset.append(row)

        return dataset

    def _read_csv_dataset(self, filename):
        dataset = []

        return dataset

    def getUnlabelledData(self, filename):
        "Se lee un archivo Excel con las ofertas a clasificar"

        with open_filename(filename, 'rb') as f:
            path = OSPath(f.name)
            if path.suffix == '.xlsx':
                dataset = self._read_excel_dataset(f)
            else:
                # Assume csv
                dataset = self._read_csv_dataset(f)

        return self.clean_dataset(dataset)
