#Este fichero contendrá las constantes que usaremos a lo largo de la practica
#por conveniencia REVISAR la guia de estilos de python https://www.python.org/dev/peps/pep-0008/
#para que todos sigamos un estilo más o menos común:
import helpers.modelFileHelper as mh

#Clave para acceder al file helper del fichero Train
TRAIN_KEY = "train"
# Clave para acceder al file helper del fichero Test
TEST_KEY = "test"
# Diccionario que contiene los ficheros CSV bajo las claves. Pueden ser accedidos mediante las claves train y test 
CSV_FILES = { TRAIN_KEY : mh.ModelFileHelper("data_sources/train.csv"), TEST_KEY :   mh.ModelFileHelper("data_sources/test.csv")} 
