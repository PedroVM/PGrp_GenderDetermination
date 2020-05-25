import difflib 
import pandas 
import numpy as np 
#define a class to help us with the process
class ModelFileHelper(object):
    """Ayuda a dar una descripcion de un fichero y a su carga """
    def __init__(self, csvFile):
     self.csvFile= pandas.read_csv(csvFile) 
     self.fileName=csvFile
    def getDescription(self):
        return self.csvFile.describe()

    def dropColumn(self, columnName):
        """wrapper para eliminar una columna"""
        self.csvFile= self.csvFile.drop(columnName, axis=1)

    def getModelTypeDetail(self):
        """Retorna una estructura legible con los tipos de dato del conjunto de datos del csv cargado"""
        return self.__translateTypestoHumanReadable(self.csvFile.dtypes)

    def findDifferences(self, other):
        """Retorna una lista con la comparacion de las columnas y los tipos de dos csv"""
        returnlist = list (difflib.Differ().compare(self.getModelTypeDetail().to_string().splitlines(1), other.getModelTypeDetail().to_string().splitlines(1)))
        returnlist.append("Comparativa de tamaños: ")
        returnlist.append (self.fileName +  " Filas:" + ''.join(self.__tuplaCleanUp(self.csvFile.shape[0:1])) + " Columnas:" +  ''.join(self.__tuplaCleanUp(self.csvFile.shape[1:2])))
        returnlist.append (other.fileName + " Filas:" + ''.join(self.__tuplaCleanUp(other.csvFile.shape[0:1])) + " Columnas:" +  ''.join(self.__tuplaCleanUp(other.csvFile.shape[1:2])))
        return returnlist

    def pearson(self,  A,  B):
        """ indice de coorrelacion lineal de Pearson de la variable A con respecto a variable B. 
        Acotado entre [1 , -1] indicando |1| alta coorrelacion y en el caso de ser negativo el coeficiente, correlación inversa """
        pearson = self.csvFile[A].corr(self.csvFile[B])
        direccion = "directa" if (pearson>0) else ("inversa" if pearson < 0 else "No existe")
        return "Correlación lineal [" + direccion + "]: " + str( abs(pearson) )

    def exportHarmonizatedModel(self, harmonizationMatrix, harmonizationquery, fileName):
        """Exporta el modelo tras armonizar los valores en funcion de una matriz de armonización dada y una query"""
        harmonizated =self.csvFile 
        dataframe = pandas.DataFrame(harmonizationMatrix)
        for index, trainedRow in dataframe.iterrows() :
            group =harmonizated.query(harmonizationquery) 
            for index, groupRow in  group.iterrows():
                randomVal= np.random.randint(trainedRow['Min'], trainedRow['Max'])
                harmonizated.loc[(harmonizated.PassengerId  ==  groupRow.PassengerId) , "Age"]=randomVal
        #dump to csv
        print ("volcando a archivo harmonizated_train.csv")
        harmonizated.to_csv(fileName,  index=False)  


    def __tuplaCleanUp(self, tupla):
        result = str(tupla).replace('(','').replace(')','').replace(',','')
        return result

    def __translateTypestoHumanReadable(self, text):
        return text.replace("int64", "Numero").replace("object", "Cadena de texto AlfaNumerica").replace("float64", "Numero (largo)")