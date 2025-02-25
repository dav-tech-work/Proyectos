from word_auto import WordAuto

doc =  WordAuto("resumen.docx")  # Crear una instancia de la clase WordAuto
doc.add_paragraph("Este es un resumen automático.")  # Agregar un párrafo al documento
doc.save_document()  # Guardar el documento



