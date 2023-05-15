import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc


class MainWindow(qtw.QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Arte & Arquitectura')

        # self.showFullScreen()

        self.title = qtw.QLabel('Presupuesto')
        self.presupuestos_pendientes = qtw.QComboBox()
        self.clientes_combo = qtw.QComboBox()
        self.trabajos_todos = qtw.QComboBox()
        self.trabajos_año = qtw.QComboBox()

        self.cliente = qtw.QLineEdit()
        self.motivo = qtw.QLineEdit()
        self.cantidad = qtw.QLineEdit()
        self.med_orig_cm_alto = qtw.QLineEdit()
        self.med_orig_cm_ancho = qtw.QLineEdit()
        self.med_final_cm_alto = qtw.QLineEdit()
        self.med_final_cm_ancho = qtw.QLineEdit()
        self.pp_cm = qtw.QLineEdit()
        self.var = qtw.QLineEdit()
        self.sup_m2 = qtw.QLineEdit()
        self.per_ml = qtw.QLineEdit()

        self.fecha_rec = qtw.QLineEdit()
        self.fecha_entrega = qtw.QLineEdit()
        self.fecha_realizacion = qtw.QLineEdit()

        #### Detalle ####
        # Col 1
        self.label_nombre = qtw.QLabel('Nombre del producto')
        self.combo1 = qtw.QComboBox()
        self.combo2 = qtw.QComboBox()
        self.combo3 = qtw.QComboBox()
        self.combo4 = qtw.QComboBox()
        self.combo5 = qtw.QComboBox()
        self.combo6 = qtw.QComboBox()
        self.combo7 = qtw.QComboBox()
        self.combo8 = qtw.QComboBox()

        # Col 2
        self.label_stock = qtw.QLabel('Stock')
        self.stock1 = qtw.QLineEdit()
        self.stock2 = qtw.QLineEdit()
        self.stock3 = qtw.QLineEdit()
        self.stock4 = qtw.QLineEdit()
        self.stock5 = qtw.QLineEdit()
        self.stock6 = qtw.QLineEdit()
        self.stock7 = qtw.QLineEdit()
        self.stock8 = qtw.QLineEdit()

        # Col 3
        self.label_p_unitario = qtw.QLabel('P. Unitario')
        self.punitario1 = qtw.QLineEdit()
        self.punitario2 = qtw.QLineEdit()
        self.punitario3 = qtw.QLineEdit()
        self.punitario4 = qtw.QLineEdit()
        self.punitario5 = qtw.QLineEdit()
        self.punitario6 = qtw.QLineEdit()
        self.punitario7 = qtw.QLineEdit()
        self.punitario8 = qtw.QLineEdit()

        # Col 4
        self.label_total = qtw.QLabel('Total')
        self.total1 = qtw.QLineEdit()
        self.total2 = qtw.QLineEdit()
        self.total3 = qtw.QLineEdit()
        self.total4 = qtw.QLineEdit()
        self.total5 = qtw.QLineEdit()
        self.total6 = qtw.QLineEdit()
        self.total7 = qtw.QLineEdit()
        self.total8 = qtw.QLineEdit()

        # Totales
        self.label_p_unitario2 = qtw.QLabel('P. Unitario',
                                            objectName='preciounitariolabel')
        self.label_total2 = qtw.QLabel('Total',
                                       objectName='preciototallabel')
        self.punit = qtw.QLabel('0.00', objectName='preciounitario')
        self.total = qtw.QLabel('0.00', objectName='preciototal')

        # Otros
        self.otro1 = qtw.QLineEdit()
        self.otro2 = qtw.QLineEdit()
        self.otro3 = qtw.QLineEdit()

        self.p_otro1 = qtw.QLineEdit()
        self.p_otro2 = qtw.QLineEdit()
        self.p_otro3 = qtw.QLineEdit()

        # Botones
        self.btn_borrar = qtw.QPushButton('Borrar',
                                          objectName='botonborrar')
        self.btn_pdf = qtw.QPushButton('PDF',
                                       objectName='botonpdf')
        self.btn_eliminar_todo = qtw.QPushButton('Descartar presupuesto',
                                                 objectName='borrartodo')

        # Layout
        main_layout = qtw.QVBoxLayout()
        grid1 = qtw.QGridLayout()
        grid2 = qtw.QGridLayout()
        box1 = qtw.QGroupBox(' ')
        self.setLayout(main_layout)
        main_layout.addLayout(grid1)
        grid1.addWidget(self.title, 0, 0, 1, 4)
        grid1.addWidget(qtw.QLabel('Presupuestos pendientes'),
                              1, 1)
        grid1.addWidget(self.presupuestos_pendientes, 1, 2)
        grid1.addWidget(qtw.QLabel('Clientes'), 2, 1)
        grid1.addWidget(self.clientes_combo, 2, 2)
        grid1.addWidget(qtw.QLabel('Trabajos (todos)'), 1, 3)
        grid1.addWidget(self.trabajos_todos, 1, 4)
        grid1.addWidget(qtw.QLabel('Trabajos (por año)'), 2, 3)
        grid1.addWidget(self.trabajos_año, 2, 4)
        # main_layout.addLayout(qtw.QSpacerItem(1, 1), 4, 1, 1, 6)
        grid2.addWidget(qtw.QLabel('Cliente'), 1, 1)
        grid2.addWidget(self.cliente, 1, 2, 1, 2)
        grid2.addWidget(qtw.QLabel('Motivo'), 2, 1)
        grid2.addWidget(self.motivo, 2, 2, 1, 2)
        grid2.addWidget(qtw.QLabel('Cant.'), 1, 4)
        grid2.addWidget(self.cantidad, 2, 4, 1, 1)

        # Fechas
        grid2.addItem(qtw.QSpacerItem(10, 20), 3, 1)
        grid2.addWidget(qtw.QLabel('Fecha Recepción'), 4, 1)
        grid2.addWidget(self.fecha_rec, 4, 2)
        grid2.addWidget(qtw.QLabel('Fecha Entrega'), 5, 1)
        grid2.addWidget(self.fecha_entrega, 5, 2)
        grid2.addWidget(qtw.QLabel('Fecha Realización'), 4, 3)
        grid2.addWidget(self.fecha_realizacion, 5, 3)

        # Carga de producto
        grid2.addItem(qtw.QSpacerItem(10, 20), 6, 1)
        # box1.setLayout(grid1)
        grid2.addWidget(self.label_nombre, 7, 1)
        grid2.addWidget(self.combo1, 8, 1, 1, 4)
        grid2.addWidget(self.combo2, 9, 1, 1, 4)
        grid2.addWidget(self.combo3, 10, 1, 1, 4)
        grid2.addWidget(self.combo4, 11, 1, 1, 4)
        grid2.addWidget(self.combo5, 12, 1, 1, 4)
        grid2.addWidget(self.combo6, 13, 1, 1, 4)
        grid2.addWidget(self.combo7, 14, 1, 1, 4)
        grid2.addWidget(self.combo8, 15, 1, 1, 4)
        # Stock
        grid2.addWidget(self.label_stock, 7, 5)
        grid2.addWidget(self.stock1, 8, 5)
        grid2.addWidget(self.stock2, 9, 5)
        grid2.addWidget(self.stock3, 10, 5)
        grid2.addWidget(self.stock4, 11, 5)
        grid2.addWidget(self.stock5, 12, 5)
        grid2.addWidget(self.stock6, 13, 5)
        grid2.addWidget(self.stock7, 14, 5)
        grid2.addWidget(self.stock8, 15, 5)
        # P. Unitario
        grid2.addWidget(self.label_p_unitario, 7, 6)
        grid2.addWidget(self.punitario1, 8, 6)
        grid2.addWidget(self.punitario2, 9, 6)
        grid2.addWidget(self.punitario3, 10, 6)
        grid2.addWidget(self.punitario4, 11, 6)
        grid2.addWidget(self.punitario5, 12, 6)
        grid2.addWidget(self.punitario6, 13, 6)
        grid2.addWidget(self.punitario7, 14, 6)
        grid2.addWidget(self.punitario8, 15, 6)
        # Total
        grid2.addWidget(self.label_total, 7, 7)
        grid2.addWidget(self.total1, 8, 7)
        grid2.addWidget(self.total2, 9, 7)
        grid2.addWidget(self.total3, 10, 7)
        grid2.addWidget(self.total4, 11, 7)
        grid2.addWidget(self.total5, 12, 7)
        grid2.addWidget(self.total6, 13, 7)
        grid2.addWidget(self.total7, 14, 7)
        grid2.addWidget(self.total8, 15, 7)
        # Otros
        grid2.addItem(qtw.QSpacerItem(10, 20), 16, 1)
        grid2.addWidget(self.otro1, 17, 1, 1, 5)
        grid2.addWidget(self.otro2, 18, 1, 1, 5)
        grid2.addWidget(self.otro3, 19, 1, 1, 5)
        grid2.addWidget(self.p_otro1, 17, 7)
        grid2.addWidget(self.p_otro2, 18, 7)
        grid2.addWidget(self.p_otro3, 19, 7)

        grid2.addWidget(self.label_p_unitario2, 7, 8, 1, 2)
        grid2.addWidget(self.punit, 9, 8, 2, 2)
        grid2.addWidget(self.label_total2, 7, 10, 1, 2)
        grid2.addWidget(self.total, 9, 10, 2, 2)
        grid2.addWidget(self.btn_borrar, 11, 9, 2, 2)
        main_layout.addSpacerItem(qtw.QSpacerItem(10, 30))
        main_layout.addLayout(grid2)

        self.show()


stylesheet = '''
QWidget {
    background-color: darkcyan;
    }
QLabel {
font-size: 11pt;
}
#preciounitario {
border: 3px solid gray;
background-color: gray;
border-style:outset;
border-width:3px;
border-color:yellow;
font-size: 17pt;
}
#preciototal {
border: 3px solid gray;
background-color: gray;
border-style:outset;
border-width:3px;
border-color:yellow;
font-size: 17pt;
}
QLineEdit {
    border: 1px solid black;
    background-color: lightgray;
}
QComboBox {
background-color: cadetblue;
}
QPushButton {
border-style: outset;
border-width: 3px;
border-color: cadetblue;
font-size: 11pt;
padding: 6px;
}
'''
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = MainWindow()
    sys.exit(app.exec())
