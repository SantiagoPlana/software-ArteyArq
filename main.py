import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
import pandas as pd


class MainWindow(qtw.QWidget):

    presupuesto = pd.read_csv('database/DB/presupuesto.csv', sep=',')
    productos = pd.read_csv('database/DB/productos.csv', sep=',')

    def __init__(self):

        super().__init__()

        self.setWindowTitle('Arte & Arquitectura')

        # self.showFullScreen()

        self.title = qtw.QLabel('Presupuesto', objectName='titulo')
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
        self.med_final_cm_ancho.setText('0')
        self.med_final_cm_alto.setText('0')
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
        self.grid1 = qtw.QGridLayout(objectName='grid1')
        self.grid2 = qtw.QGridLayout()
        box1 = qtw.QGroupBox(' ')
        self.setLayout(main_layout)
        main_layout.addLayout(self.grid1)
        self.grid1.addWidget(self.title, 0, 0, 1, 2)
        self.grid1.addWidget(qtw.QLabel('Presupuestos pendientes'), 1, 1)
        self.grid1.addWidget(self.presupuestos_pendientes, 1, 2)
        self.grid1.addWidget(qtw.QLabel('Clientes'), 2, 1)
        self.grid1.addWidget(self.clientes_combo, 2, 2)
        self.grid1.addWidget(qtw.QLabel('Trabajos (todos)'), 1, 3)
        self.grid1.addWidget(self.trabajos_todos, 1, 4)
        self.grid1.addWidget(qtw.QLabel('Trabajos (por año)'), 2, 3)
        self.grid1.addWidget(self.trabajos_año, 2, 4)
        # main_layout.addLayout(qtw.QSpacerItem(1, 1), 4, 1, 1, 6)
        self.grid2.addWidget(qtw.QLabel('Cliente'), 1, 1)
        self.grid2.addWidget(self.cliente, 1, 2, 1, 2)
        self.grid2.addWidget(qtw.QLabel('Motivo'), 2, 1)
        self.grid2.addWidget(self.motivo, 2, 2, 1, 2)
        self.grid2.addWidget(qtw.QLabel('Cant.'), 1, 4)
        self.grid2.addWidget(self.cantidad, 2, 4, 1, 1)

        # Fechas
        self.grid2.addItem(qtw.QSpacerItem(10, 20), 3, 1)
        self.grid2.addWidget(qtw.QLabel('Fecha Recepción'), 4, 1)
        self.grid2.addWidget(self.fecha_rec, 4, 2)
        self.grid2.addWidget(qtw.QLabel('Fecha Entrega'), 5, 1)
        self.grid2.addWidget(self.fecha_entrega, 5, 2)
        self.grid2.addWidget(qtw.QLabel('Fecha Realización'), 4, 3)
        self.grid2.addWidget(self.fecha_realizacion, 5, 3)

        # Medidas
        self.grid2.addWidget(qtw.QLabel('Med. Orig. cm.'), 1, 6, 2, 1)
        self.grid2.addWidget(self.med_orig_cm_ancho, 1, 7)
        self.grid2.addWidget(self.med_orig_cm_alto, 2, 7)

        self.grid2.addWidget(qtw.QLabel('pp. cm'), 1, 8)
        self.grid2.addWidget(self.pp_cm, 1, 9)
        self.grid2.addWidget(qtw.QLabel('var.'), 2, 8)
        self.grid2.addWidget(self.var, 2, 9)

        self.grid2.addWidget(qtw.QLabel('Med. Final cm.'), 4, 6, 2, 1)
        self.grid2.addWidget(self.med_final_cm_ancho, 4, 7)
        self.grid2.addWidget(self.med_final_cm_alto, 5, 7)

        self.grid2.addWidget(qtw.QLabel('Sup. m2:'), 4, 8)
        self.grid2.addWidget(self.sup_m2, 4, 9)
        self.grid2.addWidget(qtw.QLabel('Per. ml:'), 5, 8)
        self.grid2.addWidget(self.per_ml, 5, 9)
        # Carga de producto
        self.grid2.addItem(qtw.QSpacerItem(10, 20), 6, 1)
        # box1.setLayout(grid1)
        self.grid2.addWidget(self.label_nombre, 7, 1)
        self.grid2.addWidget(self.combo1, 8, 1, 1, 4)
        self.grid2.addWidget(self.combo2, 9, 1, 1, 4)
        self.grid2.addWidget(self.combo3, 10, 1, 1, 4)
        self.grid2.addWidget(self.combo4, 11, 1, 1, 4)
        self.grid2.addWidget(self.combo5, 12, 1, 1, 4)
        self.grid2.addWidget(self.combo6, 13, 1, 1, 4)
        self.grid2.addWidget(self.combo7, 14, 1, 1, 4)
        self.grid2.addWidget(self.combo8, 15, 1, 1, 4)
        # Stock
        self.grid2.addWidget(self.label_stock, 7, 5)
        self.grid2.addWidget(self.stock1, 8, 5)
        self.grid2.addWidget(self.stock2, 9, 5)
        self.grid2.addWidget(self.stock3, 10, 5)
        self.grid2.addWidget(self.stock4, 11, 5)
        self.grid2.addWidget(self.stock5, 12, 5)
        self.grid2.addWidget(self.stock6, 13, 5)
        self.grid2.addWidget(self.stock7, 14, 5)
        self.grid2.addWidget(self.stock8, 15, 5)
        # P. Unitario
        self.grid2.addWidget(self.label_p_unitario, 7, 6)
        self.grid2.addWidget(self.punitario1, 8, 6)
        self.grid2.addWidget(self.punitario2, 9, 6)
        self.grid2.addWidget(self.punitario3, 10, 6)
        self.grid2.addWidget(self.punitario4, 11, 6)
        self.grid2.addWidget(self.punitario5, 12, 6)
        self.grid2.addWidget(self.punitario6, 13, 6)
        self.grid2.addWidget(self.punitario7, 14, 6)
        self.grid2.addWidget(self.punitario8, 15, 6)
        # Total
        self.grid2.addWidget(self.label_total, 7, 7)
        self.grid2.addWidget(self.total1, 8, 7)
        self.grid2.addWidget(self.total2, 9, 7)
        self.grid2.addWidget(self.total3, 10, 7)
        self.grid2.addWidget(self.total4, 11, 7)
        self.grid2.addWidget(self.total5, 12, 7)
        self.grid2.addWidget(self.total6, 13, 7)
        self.grid2.addWidget(self.total7, 14, 7)
        self.grid2.addWidget(self.total8, 15, 7)
        # Otros
        self.grid2.addItem(qtw.QSpacerItem(10, 20), 16, 1)
        self.grid2.addWidget(self.otro1, 17, 1, 1, 5)
        self.grid2.addWidget(self.otro2, 18, 1, 1, 5)
        self.grid2.addWidget(self.otro3, 19, 1, 1, 5)
        self.grid2.addWidget(self.p_otro1, 17, 7)
        self.grid2.addWidget(self.p_otro2, 18, 7)
        self.grid2.addWidget(self.p_otro3, 19, 7)

        self.grid2.addWidget(self.label_p_unitario2, 7, 8, 1, 2)
        self.grid2.addWidget(self.punit, 9, 8, 2, 2)
        self.grid2.addWidget(self.label_total2, 7, 10, 1, 2)
        self.grid2.addWidget(self.total, 9, 10, 2, 2)
        self.grid2.addWidget(self.btn_borrar, 11, 9, 2, 2)
        main_layout.addSpacerItem(qtw.QSpacerItem(10, 30))
        main_layout.addLayout(self.grid2)

        #### Combo-boxes ####
        ### Clientes

        self.completer_trabajos = qtw.QCompleter(
            self.presupuesto.loc[:, 'Motivo'], self
        )
        self.completer_trabajos.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_trabajos.setFilterMode(qtc.Qt.MatchContains)
        self.completer_clientes = qtw.QCompleter(
            self.presupuesto.loc[:, 'Cliente'], self
        )
        self.completer_clientes.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_clientes.setFilterMode(qtc.Qt.MatchContains)

        self.clientes_combo.addItem('')
        self.clientes_combo.addItems(
            sorted(self.presupuesto.loc[:, 'Cliente'].unique()))
        self.trabajos_todos.addItem('')
        self.trabajos_todos.addItems(
            sorted(self.presupuesto.loc[:, 'Motivo'].unique())
        )
        self.trabajos_todos.setEditable(True)
        self.clientes_combo.setEditable(True)
        self.trabajos_todos.setCompleter(self.completer_trabajos)
        self.clientes_combo.setCompleter(self.completer_clientes)


        # Productos
        # Instanciamos completers
        # Lamentablemente hay que setear un completer por combobox o si no se borran los valores de uno
        # cuando se modifica otro...
        self.completer_productos = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos.setFilterMode(qtc.Qt.MatchContains)
        self.completer_productos2 = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos2.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos2.setFilterMode(qtc.Qt.MatchContains)
        self.completer_productos3 = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos3.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos3.setFilterMode(qtc.Qt.MatchContains)
        self.completer_productos4 = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos4.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos4.setFilterMode(qtc.Qt.MatchContains)
        self.completer_productos5 = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos5.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos5.setFilterMode(qtc.Qt.MatchContains)
        self.completer_productos6 = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos6.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos6.setFilterMode(qtc.Qt.MatchContains)
        self.completer_productos7 = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos7.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos7.setFilterMode(qtc.Qt.MatchContains)
        self.completer_productos8 = qtw.QCompleter(
            self.productos.loc[:, 'DenominaciónCompleta'], self)
        self.completer_productos8.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_productos8.setFilterMode(qtc.Qt.MatchContains)


        # Setting editability and completer for each product combo-box
        self.combo1.setEditable(True)
        self.combo2.setEditable(True)
        self.combo3.setEditable(True)
        self.combo4.setEditable(True)
        self.combo5.setEditable(True)
        self.combo6.setEditable(True)
        self.combo7.setEditable(True)
        self.combo8.setEditable(True)
        self.combo1.setCompleter(self.completer_productos)
        self.combo2.setCompleter(self.completer_productos2)
        self.combo3.setCompleter(self.completer_productos3)
        self.combo4.setCompleter(self.completer_productos4)
        self.combo5.setCompleter(self.completer_productos5)
        self.combo6.setCompleter(self.completer_productos6)
        self.combo7.setCompleter(self.completer_productos7)
        self.combo8.setCompleter(self.completer_productos8)

        # Signals
        self.combo1.activated.connect(lambda: self.complete_products(string=self.combo1.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo1)))
        self.combo2.activated.connect(lambda: self.complete_products(string=self.combo2.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo2)))
        self.combo3.activated.connect(lambda: self.complete_products(string=self.combo3.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo3)))
        self.combo4.activated.connect(lambda: self.complete_products(string=self.combo4.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo4)))
        self.combo5.activated.connect(lambda: self.complete_products(string=self.combo5.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo5)))
        self.combo6.activated.connect(lambda: self.complete_products(string=self.combo6.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo6)))
        self.combo7.activated.connect(lambda: self.complete_products(string=self.combo7.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo7)))
        self.combo8.activated.connect(lambda: self.complete_products(string=self.combo8.currentText(),
                                                                     idx=self.grid2.indexOf(self.combo8)))

        # Borrar
        self.btn_borrar.clicked.connect(self.borrar)

        # Medidas
        self.med_orig_cm_ancho.textChanged.connect(self.calculo_medidas)
        self.med_orig_cm_alto.textChanged.connect(self.calculo_medidas)
        self.pp_cm.textChanged.connect(self.calculo_medidas)
        self.var.textChanged.connect(self.calculo_medidas)
        self.show()

    # Methods
    # Form methods
    def complete_products(self, string, idx):
        subset = self.productos[
            self.productos['DenominaciónCompleta'] == string]
        row, column, cols, rows = self.grid2.getItemPosition(idx)
        stock = self.grid2.itemAtPosition(row, 5).widget()
        p_unit = self.grid2.itemAtPosition(row, 6).widget()
        total = self.grid2.itemAtPosition(row, 7).widget()
        try:
            stock.setText(str(subset.loc[:, 'Stock'].values[0]))
            p_unit.setText(str(subset.loc[:, 'PrecioUnidad'].values[0]))
        except Exception as e:
            pass

    # !Pendiente
    def complete_from_client(self, string):
        # Hace falta aclaración con respecto de los datos antes de implementar este método
        subset = self.presupuesto[
            self.presupuesto['Cliente'] == string
        ]
        self.fecha_rec.setText(subset['F_Recepción'].values[0])
        self.fecha_entrega.setText(subset['F_Eentrega'].values[0])
        self.fecha_realizacion.setText(subset['F_Realización'].values[0])
        self.motivo.setText(subset['Motivo'].values[0])
        for row in range(self.grid2.rowCount()):
            if row == 7:
                item = self.grid2.itemAtPosition(row, 0).widget()
    # !Pendiente
    def complete_from_work(self):
        pass

    @qtc.pyqtSlot()
    def borrar(self):
        for i in range(self.grid1.count()):
            item = self.grid1.itemAt(i).widget()
            if isinstance(item, qtw.QComboBox):
                item.clearEditText()
        for i in range(self.grid2.count()):
            item = self.grid2.itemAt(i).widget()
            if isinstance(item, qtw.QComboBox):
                item.clearEditText()
            elif isinstance(item, qtw.QLineEdit):
                item.clear()
        self.med_final_cm_ancho.setText('0')
        self.med_final_cm_alto.setText('0')

    # Cálculos
    @qtc.pyqtSlot()
    def calculo_medidas(self):
        if len(self.med_orig_cm_ancho.text()) > 0 and len(self.med_orig_cm_alto.text()) > 0:
            cm_ancho = float(self.med_orig_cm_ancho.text())
            cm_alto = float(self.med_orig_cm_alto.text())
        elif len(self.med_orig_cm_ancho.text()) > 0 and len(self.med_orig_cm_alto.text()) < 1:
            cm_ancho = float(self.med_orig_cm_ancho.text())
            cm_alto = 0
        elif len(self.med_orig_cm_ancho.text()) < 1 and len(self.med_orig_cm_alto.text()) > 0:
            cm_ancho = 0
            cm_alto = float(self.med_orig_cm_alto.text())
        else:
            cm_ancho = 0
            cm_alto = 0
        # check pp y var
        if len(self.pp_cm.text()) > 0 and len(self.var.text()) > 0:
            pp = float(self.pp_cm.text()) * 2
            var = float(self.var.text()) * 2
        elif len(self.pp_cm.text()) > 0 and len(self.var.text()) < 1:
            pp = float(self.pp_cm.text()) * 2
            var = 0
        elif len(self.pp_cm.text()) < 1 and len(self.var.text()) > 0:
            pp = 0
            var = float(self.var.text()) * 2
        else:
            pp = 0
            var = 0
        final_ancho = cm_ancho + pp + var
        final_alto = cm_alto + pp + var
        self.med_final_cm_ancho.setText(str(final_ancho))
        self.med_final_cm_alto.setText(str(final_alto))
        # Superficie (m2)
        if len(self.pp_cm.text()) > 0:
            sup = (float(self.med_final_cm_ancho.text()) / 100 *
                   float(self.med_final_cm_alto.text()) / 100)
            self.sup_m2.setText(str(sup))
        else:
            self.sup_m2.clear()
        # Perímetro (mm)
        # instructions or desired functionality unclear
        if len(self.var.text()) > 0:
            per = (float(self.med_final_cm_ancho.text()) +
                   float(self.med_final_cm_alto.text()) * 2) / 1000
            self.per_ml.setText(str(per))
        else:
            self.var.clear()

    
stylesheet = '''

#titulo {
color: #000115;
font: bold;
font-size: 22pt;
font-family: Trebuchet MS;
}
QWidget {
    background-color: antiquewhite;
    }

QLabel {
font-size: 11pt;
color: #000115;
}
#preciounitario {
border: 3px solid gray;
background-color: gray;
border-style:outset;
border-width:3px;
border-color:bisque;
font-size: 17pt;
}
#preciototal {
border: 3px solid gray;
background-color: gray;
border-style:outset;
border-width:3px;
border-color:cornsilk;
font-size: 17pt;
}
QLineEdit {
    border: 1px solid black;
    background-color: lightgray;
}
QComboBox {
background-color: ivory;
}
QPushButton {
border-style: outset;
border-width: 3px;
border-color: #000115;
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
