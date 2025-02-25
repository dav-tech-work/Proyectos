"""
Extrar los datos de un archivo de excel y mostrarlos en una tabla de word

"""

import pandas as pd
from docx import Document
# Cargar el archivo Excel
df = pd.read_excel('datos.xlsx')
# Crear un nuevo documento de Word  
doc = Document()    
# Agregar la tabla al documento
table = doc.add_table(rows=1, cols=len(df.columns)) # Creación de la tabla con los encabezados del dataframe

# Añadir encabezados a la tabla
table.cell(0, 0).text = df.columns[0] # Asignar el nombre de las columnas al encabezado de la tabla
hdr_cells = table.rows[0].cells 

for i, col in enumerate(df.columns):
    hdr_cells[i].text = col

for index, row in df.iterrows(): # Iteración sobre cada fila del dataframe
    row_cells = table.add_row().cells 
    for cell_value in row: # Iteración sobre cada celda de la fila
        row_cells[0].text = str(cell_value) # Asignar el valor de la celda a la tabla

# Guardar el documento de Word
doc.save('datos.docx')









