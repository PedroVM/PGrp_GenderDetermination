import difflib 
import pandas as pd
import numpy as np
import shared.supportedFiles as const


#define a class to help us with the process

class ModelFileHelper(object):
    '''Ayuda a dar una descripcion de un fichero y a su carga '''
    def __init__(self, csvFile):
        self.__configurePandas()
        self.csvFile= pd.read_csv(csvFile) 
        self.fileName=csvFile
        self.ColumnDescriptions ={}
    def getDescription(self):
        return self.csvFile.describe()

    def setColumDescriptionsFile(self, fileFormat, filepath, columnkeyIndex=0, removeNotFoundColumns=True , excelSheet=0):
        ''' vincula las descripciones de las columnas del csv a las descripciones existentes en un fichero adicional.
        fileFormat, usar la enumeracion SupportedFiles
        filepath es el fichero diccionario.
        columnKeyIndex el índice de columna que contiene el nombre de las columnas.
        removeNotFoundColumns elimina del csv cargado en el helper aquellas columnas no encontradas en el csv diccionario.
        el metodo retorna una lista con las columnas eliminadas cuando removeNotFoundColumns es verdadero.
        el metodo retorna una lista con las columnas No encontradas en el csv de datos cuando removeNotFoundColumns es falso.
        excelSheet por defecto 0 es la hoja excel de donde queremos cargar los datos '''

        dataFrame = self.__readFileFormat(filepath,fileFormat,excelSheet)
        #leer y montar en un diccionario key-value donde value es un join del resto de las columnas que no son el columnIndex
        for index, row in dataFrame.iterrows():
            self.ColumnDescriptions[row[columnkeyIndex]] = "".join(row[columnkeyIndex:])

         #ver que columnas existen y qué columnas no   
        resultado = [] 
        for columnName in self.csvFile.columns:
            if not columnName in self.ColumnDescriptions:
                item = columnName  + " No encontrada en CSV de datos "
                if (removeNotFoundColumns):
                    #eliminar columna
                    resultado.append( item + "Accion: Eliminada")
                    self.dropColumn(columnName)
                else:
                    #no eliminar, informar.
                    resultado.append( item + "Accion: Ninguna")
        
        return resultado             

    def dropColumn(self, columnName):
        '''wrapper para eliminar una columna'''
        self.csvFile= self.csvFile.drop(columnName, axis=1)

    def getModelTypeDetail(self, fileName=None):
        '''Retorna una estructura legible con los tipos de dato del conjunto de datos del csv cargado
             exporta la salida a filename si se proporciona un nombre de fichero '''
        if (fileName==None) :    
            return self.__translateTypestoHumanReadable(self.csvFile.dtypes)
        else:
            with open( fileName, 'w') as f:
               
               print(self.__translateTypestoHumanReadable(self.csvFile.dtypes), file=f)     

    def findDifferences(self, other):
        '''Retorna una lista con la comparacion de las columnas y los tipos de dos csv'''
        returnlist = list (difflib.Differ().compare(self.getModelTypeDetail().to_string().splitlines(1), other.getModelTypeDetail().to_string().splitlines(1)))
        returnlist.append("Comparativa de tamaños: ")
        returnlist.append (self.fileName +  " Filas:" + ''.join(self.__tuplaCleanUp(self.csvFile.shape[0:1])) + " Columnas:" +  ''.join(self.__tuplaCleanUp(self.csvFile.shape[1:2])))
        returnlist.append (other.fileName + " Filas:" + ''.join(self.__tuplaCleanUp(other.csvFile.shape[0:1])) + " Columnas:" +  ''.join(self.__tuplaCleanUp(other.csvFile.shape[1:2])))
        return returnlist

    def pearson(self,  A,  B):
        ''' indice de coorrelacion lineal de Pearson de la variable A con respecto a variable B. 
        Acotado entre [1 , -1] indicando |1| alta coorrelacion y en el caso de ser negativo el coeficiente, correlación inversa '''
        pearson = self.csvFile[A].corr(self.csvFile[B])
        direccion = "directa" if (pearson>0) else ("inversa" if pearson < 0 else "No existe")
        return "Correlación lineal [" + direccion + "]: " + str( abs(pearson) )

    def exportHarmonizatedModel(self, harmonizationMatrix, harmonizationquery, fileName):
        '''Exporta el modelo tras armonizar los valores en funcion de una matriz de armonización dada y una query'''
        harmonizated =self.csvFile 
        dataframe = pd.DataFrame(harmonizationMatrix)
        for index, trainedRow in dataframe.iterrows() :
            group =harmonizated.query(harmonizationquery) 
            for index, groupRow in  group.iterrows():
                randomVal= np.random.randint(trainedRow['Min'], trainedRow['Max'])
                harmonizated.loc[(harmonizated.PassengerId  ==  groupRow.PassengerId) , "Age"]=randomVal
        #dump to csv
        print ("volcando a archivo harmonizated_train.csv")
        harmonizated.to_csv(fileName,  index=False)  

    def nullCounts(self):
        ''' Vuelca informacion sobre el numero de valores nulos en las diferentes columnas '''
        self.csvFile.info(verbose=True, null_counts=True)

    def getNullPercents(self):
        ''' Recupera un diccionario donde las claves son los nombres y de columna y los valores un diccionario anexado
        con clave '%' para el % de valores nulos y 'description' para obtener la descripcion de la variable (diccionario) '''
        total_rows = self.csvFile.shape[0] #(rows, colums)
        result ={}
        for  column in self.csvFile.loc[:, self.csvFile.isnull().any()] :
            notnullValues= self.csvFile[column].count()
            #key -> (%,Descripcion)
            result[column]={ '%' :100 * float(total_rows-notnullValues) / float(total_rows), 'description': self.ColumnDescriptions[column]}
        return sorted(result.items(), key= lambda x: x[1]['%'], reverse=True ) 

    def removeColumnsHavingNulls(self, threshold):
        ''' Elimina las columnas que tienen un umbral de nulos por encima del proporcionado '''
        removedItems=[]
        removable = [x for x in self.getNullPercents() if x[1]['%'] >= threshold ]
        for column in removable:
            self.dropColumn(column[0])
            removedItems.append("Removed " + column[0] + " having a " + str(column[1]['%']) + " Percent of nulls"  )
        return removedItems

    def __tuplaCleanUp(self, tupla):
        result = str(tupla).replace('(','').replace(')','').replace(',','')
        return result

    def __translateTypestoHumanReadable(self, text):
        return text.replace("int64", "Numero").replace("object", "Cadena de texto AlfaNumerica").replace("float64", "Numero (largo)")
    
    def __readFileFormat(self, filepath, format, excelSheetIndex=0):
        if (format == const.SupportedFiles.EXCEL):
            return pd.read_excel(io= filepath, sheet_name = excelSheetIndex)
        elif (format == const.SupportedFiles.CSV):
            return pd.read_csv(filepath)
        return     
    def __configurePandas(self):
        pd.set_option('display.max_rows', 3000)
        pd.set_option('display.max_columns', 3000)

