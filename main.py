import sys
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5.QtGui import QPixmap, QDoubleValidator, QIcon, QFont, QPainter, QImage
from PyQt5.QtPrintSupport import QPrinter
# from PyQt5.QtPdf import QPdfDocument
from pdf2image import convert_from_path
import subprocess
import pandas as pd
import csv
import time
import traceback
import datetime

from PyQt5.QtWidgets import QMessageBox
from pdf import generate, orden_trabajo

start = time.perf_counter()


class Signals(qtc.QObject):

    finished = qtc.pyqtSignal()
    error = qtc.pyqtSignal(tuple)
    result = qtc.pyqtSignal(object)

class Worker(qtc.QRunnable):

    def __init__(self, fn, *args, **kwargs):
        
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

    @qtc.pyqtSlot()
    def run(self):
        """Inicializa la función"""
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()

class CargarStock(qtw.QDialog):
    """Dialog para carga de stock"""

    signalItemCargado = qtc.pyqtSignal(str)

    def __init__(self, dataframe):
        super().__init__()
        self.setWindowIcon(QIcon('png_aya.png'))
        self.setMinimumSize(500, 410)
        self.setSizeGripEnabled(True)
        self.grid = qtw.QGridLayout()
        self.grid.setSpacing(18)
        self.setLayout(self.grid)
        self.setWindowTitle('Nuevo producto')


        # self.material = qtw.QComboBox()
        # Todas line edit
        self.idcategoria = qtw.QComboBox()  # código de producto
        self.idproducto = qtw.QLineEdit()  # código numérico
        self.nombreproducto = qtw.QLineEdit() # nombre producto
        self.medida = qtw.QComboBox() # tipo de calculo para el producto
        self.precio = qtw.QLineEdit()

        self.idcategoria.setEditable(True)
        self.medida.setEditable(True)

        self.comboboxes = [self.idcategoria, self.medida]

        self.btn_cargar = qtw.QPushButton('Cargar producto', clicked=self.check_medida)
        self.btn_cancelar = qtw.QPushButton('Cancelar', clicked=self.close)


        self.grid.addWidget(qtw.QLabel("IdCategoría"), 1, 0)
        self.grid.addWidget(self.idcategoria, 2, 0)
        self.grid.addWidget(qtw.QLabel("IdProducto"), 1, 1)
        self.grid.addWidget(self.idproducto, 2, 1)
        self.grid.addWidget(qtw.QLabel('Nombre Producto'), 3, 0)
        self.grid.addWidget(self.nombreproducto, 4, 0)
        self.grid.addWidget(qtw.QLabel('Medida'), 3, 1)
        self.grid.addWidget(self.medida, 4, 1)
        self.grid.addWidget(qtw.QLabel('Precio Unitario'), 5, 0)
        self.grid.addWidget(self.precio, 6, 0)
        self.grid.addWidget(self.btn_cargar, 7, 0)
        self.grid.addWidget(self.btn_cancelar, 7, 1)


        self.onlyInt = QDoubleValidator()
        self.precio.setValidator(self.onlyInt)

        # self.material.addItems(['Pino', 'Algarrobo'])

        # cargar datos
        self.stock = dataframe

        self.lista_categorias = self.stock['IdCategoría'].dropna().astype(str).unique()
        self.lista_medidas = self.stock['Medida'].dropna().astype(str).unique()

        self.idcategoria.clear()
        self.idcategoria.addItem('')
        self.idcategoria.addItems(self.lista_categorias)

        self.medida.clear()
        self.medida.addItem('')
        self.medida.addItems(self.lista_medidas)
        self.completer_tipo = qtw.QCompleter(self.lista_categorias, self)
        self.completer_tipo.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_tipo.setFilterMode(qtc.Qt.MatchContains)
        self.idcategoria.setCompleter(self.completer_tipo)

        self.completer_medida = qtw.QCompleter(self.lista_medidas, self)
        self.completer_medida.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_medida.setFilterMode(qtc.Qt.MatchContains)
        self.medida.setCompleter(self.completer_medida)

        for completer in [self.completer_tipo, self.completer_medida]:
            self.style_completer_popup(completer)


        self.signalItemCargado.connect(self.msg_display)


    def cargar_csv(self, path):
        self.stock = pd.read_csv(path, sep=',')

    @qtc.pyqtSlot(str)
    def set_complete_tipo(self, string=str):
        ## Es esto o lo que está explicito en el constructor
        print('Signal!')
        try:
            subset = self.stock[self.stock['IdCategoría'] == string]['IdCategoría'].dropna().astype(str).unique()
            self.completer_tipo = qtw.QCompleter(subset, self)
            self.completer_tipo.setFilterMode(qtc.Qt.MatchContains)
            self.completer_tipo.setCaseSensitivity(qtc.Qt.CaseInsensitive)
            # self.idcategoria.setCompleter(self.completer_tipo)
        except Exception as e:
            print(e)
        # self.completer_tipo.activated.connect(self.set_complete_medida)

    @qtc.pyqtSlot(str)
    def set_complete_medida(self, string=str):
        # print('Signal!')
        subset = self.stock[self.stock['IdCategoría'] == string]['Medida']
        completer = qtw.QCompleter(subset, self)
        completer.setFilterMode(qtc.Qt.MatchContains)
        completer.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.medida.setCompleter(completer)

    def style_completer_popup(self, completer):
        """Apply styling to the completer popup."""
        completer.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                       "selection-background-color: #7E9EC9;"
                                                       "selection-color: solidblack;")

    def check_medida(self):
        medida = self.medida.currentText()
        medida = medida.strip(' ').upper()
        print(medida)
        if medida not in self.lista_medidas:
            string = 'Medida no válida. Seleccione una de las cuatro existentes.'
            self.msg_display(string)
        else:
            self.cargar()

    def cargar(self):
        id_categoria = self.idcategoria.currentText()
        id_producto = self.idproducto.text()
        nombre_producto = self.nombreproducto.text()
        medida = self.medida.currentText()
        precio = self.precio.text()
        # print(material, tipo, modelo, cantidad)
        if len(id_categoria) == 0 or len(id_producto) == 0 or len(nombre_producto) == 0 or len(precio) == 0:
            message = "Todos los campos deben estar completos"
            msg = qtw.QMessageBox()
            msg.setText(message)
            msg.setIcon(qtw.QMessageBox.Warning)
            msg.setWindowTitle('Datos insuficientes')
            msg.exec_()
        else:
            try:
                denom_completa = id_categoria + ' ' + id_producto + ' ' + nombre_producto
                contador = int(self.stock['Contador'].max()) + 1
                stock = 0
                long_hoja = 0
                lst = [id_categoria, id_producto, nombre_producto,
                       stock, precio, medida, contador, long_hoja, denom_completa]
                cols = self.stock.columns
                dic = {}
                for i, col in enumerate(cols):
                    dic[col] = lst[i]

                df = pd.DataFrame([dic])
                self.stock = pd.concat([self.stock, df], ignore_index=True)
                self.stock.to_csv('database/DB/productos.csv', index=False)

                self.msg_display('Listo, loco, producto cargado.')
            except Exception as e:
                print(e)

    @qtc.pyqtSlot(str)
    def msg_display(self, string):
        msg = qtw.QMessageBox()
        msg.setWindowIcon(QIcon('png_aya.png'))
        msg.setText(string)
        msg.setWindowTitle(' ')
        msg.setIcon(qtw.QMessageBox.NoIcon)
        msg.exec_()

class CsvTableModel(qtc.QAbstractTableModel):
    """The model for a CSV table."""

    def __init__(self, csv_file):
        super().__init__()
        self.filename = csv_file
        with open(self.filename, encoding='utf-8') as fh:
            csvreader = csv.reader(fh)
            self._headers = next(csvreader)
            self._data = list(csvreader)

    # Minimum necessary methods:
    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._headers)

    def data(self, index, role):
        # Add EditRole so that the cell is not cleared when editing
        if role in (qtc.Qt.DisplayRole, qtc.Qt.EditRole):
            return self._data[index.row()][index.column()]

    # Additional features methods:

    def headerData(self, section, orientation, role):

        if orientation == qtc.Qt.Horizontal and role == qtc.Qt.DisplayRole:
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role)

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()  # needs to be emitted before a sort
        self._data.sort(key=lambda x: x[column])
        if order == qtc.Qt.DescendingOrder:
            self._data.reverse()
        self.layoutChanged.emit()  # needs to be emitted after a sort

    # Methods for Read/Write

    def flags(self, index):
        return super().flags(index) | qtc.Qt.ItemIsEditable

    def setData(self, index, value, role):
        if index.isValid() and role == qtc.Qt.EditRole:
            if not value:
                return False
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        else:
            return False

    # Methods for inserting or deleting

    def insertRows(self, position, rows, parent):
        self.beginInsertRows(
            parent or qtc.QModelIndex(),
            position,
            position + rows - 1
        )

        for i in range(rows):
            default_row = [''] * len(self._headers)
            self._data.insert(position, default_row)
        self.endInsertRows()

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(
            parent or qtc.QModelIndex(),
            position,
            position + rows - 1
        )
        for i in range(rows):
            del (self._data[position])
        self.endRemoveRows()

    # method for saving
    def save_data(self):
        # commented out code below to fix issue with additional lines being added after saving csv file from the window.
        # with open(self.filename, 'w', encoding='utf-8') as fh:
        with open(self.filename, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(self._headers)
            writer.writerows(self._data)

class Tabla(qtw.QDialog):

    """Ventana para display de tablas"""

    def __init__(self, db):
        super().__init__()

        self.setWindowTitle('Tabla')
        self.resize(1320, 900)
        self.setSizeGripEnabled(True)
        self.setModal(False)
        # database
        self.db = db

        self.threadpool = qtc.QThreadPool()

        # Layouts
        self.v_layout = qtw.QVBoxLayout()
        self.h_layout = qtw.QHBoxLayout()
        self.setLayout(self.v_layout)

        # Table model
        self.table = qtw.QTableView()
        self.model = CsvTableModel(self.db)

        self.filter_proxy_model = qtc.QSortFilterProxyModel()
        self.filter_proxy_model.setFilterCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.filter_proxy_model.setFilterKeyColumn(0)

        self.table.setModel(self.filter_proxy_model)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)


        self.filter_proxy_model.setSourceModel(self.model)

        # filtros
        self.filtro = qtw.QComboBox()
        self.text_filtro = qtw.QLineEdit()
        self.filtro.addItems(self.model._headers)
        self.filtro.currentTextChanged.connect(self.cambiar_filtro)
        self.text_filtro.textChanged.connect(self.filter_proxy_model.setFilterRegExp)

        # Acciones
        self.eliminar_filas = qtw.QAction('Eliminar fila(s)', self)
        self.eliminar_filas.setShortcut('Del')
        self.eliminar_filas.triggered.connect(self.remove_rows)

        # otros widgets
        self.menubar = qtw.QMenuBar(objectName='menubar')
        self.menu_archivo = qtw.QMenu('Archivo')
        self.menu_editar = qtw.QMenu('Editar')


        self.menu_archivo.addAction('Guardar archivo', self.guardar_cambios)
        #self.menu_archivo.addAction('Eliminar fila(s)', self.remove_rows)
        self.menu_archivo.addAction(self.eliminar_filas)
        self.menu_editar.addAction('Insertar arriba', self.insert_above)
        self.menu_editar.addAction('Insertar abajo', self.insert_below)
        self.menubar.addMenu(self.menu_archivo)
        self.menubar.addMenu(self.menu_editar)

        self.layout().addWidget(self.menubar)
        self.layout().addWidget(qtw.QLabel('Filtrar por:'))
        self.v_layout.addLayout(self.h_layout)
        self.layout().addWidget(self.table)

        self.h_layout.addWidget(self.filtro)
        self.h_layout.addWidget(self.text_filtro)

        #self.table.resizeColumnsToContents()
        # style
        self.table.setStyleSheet('alternate-background-color: #C1D7D2;  background-color: #F4F4ED;'
                                 'font-size: 12pt; selection-background-color: #7E9EC9; ')
        menu_style = '''
        QMenu {
        background-color: #C1D7D2; /* Background color of the menu */
        }
        QMenu::item {
        padding: 5px 10px; /* Padding for each action */
        color: #0B1119; /* Default text color for actions */
        }
        QMenu::item:selected {
            background-color: #C1D7D2; /* Background for selected action */
            color: #E1F6E0; /* Text color for selected action */
        }        
    '''
        self.menubar.setStyleSheet('''spacing: 3px; font-size: 10pt; color: #E1F6E0; ''')

        #self.menu_archivo.setStyleSheet('''selection-background-color:#C1D7D2; color: #E1F6E0;font-size: 10pt; ''')
        #self.menu_editar.setStyleSheet('selection-background-color: #C1D7D2; color: #E1F6E0;font-size: 10pt;')
        self.menu_archivo.setStyleSheet(menu_style)
        self.menu_editar.setStyleSheet(menu_style)

        if self.db.split('/')[-1] == 'productos.csv':
            self.filtro.setCurrentIndex(8)
            self.menubar.addAction('Agregar porcentaje', self.sumar_porcentaje_dialog)
            self.menubar.addAction('Restar porcentaje', self.descontar_porcentaje_dialog)
            self.table.resizeColumnsToContents()
        else:
            self.filtro.setCurrentIndex(4)


    @qtc.pyqtSlot()
    def cambiar_filtro(self):
        index = self.filtro.currentIndex()
        self.filter_proxy_model.setFilterKeyColumn(index)

    def guardar_cambios(self):
        if self.model:
            worker = Worker(self.model.save_data)
            worker.signals.result.connect(lambda: print('funca'))
            self.threadpool.start(worker)
            # self.statusBar().showMessage('Archivo guardado correctamente', 1000)

    def insert_above(self):
        try:
            selected = self.table.selectedIndexes()
            row = selected[0].row() if selected else 0
            self.model.insertRows(row, 1, None)
        except Exception as e:
            pass

    def insert_below(self):
        try:
            selected = self.table.selectedIndexes()
            row = selected[-1].row() if selected else self.model.rowCount(None)
            self.model.insertRows(row + 1, 1, None)
        except Exception as e:
            pass

    def remove_rows(self):
        selected = self.table.selectedIndexes()
        num_rows = len(set(index.row() for index in selected))
        selected_proxy = [self.filter_proxy_model.mapToSource(idx) for idx in selected]

        if selected:
            try:
                for row in range(num_rows):
                    self.model.removeRows(selected_proxy[row].row(), num_rows, None)
            except Exception as e:
                print(str(e))

    def sumar_porcentaje_dialog(self):
        """Input dialog para ingresar porcentaje"""

        user_input = qtw.QInputDialog()

        porcentaje, ok = user_input.getDouble(self,
                                              'Porcentaje',
                                              'Porcentaje: ',
                                              qtw.QLineEdit.Normal,
                                              0, 100)
        if porcentaje and ok:
            self.sumar_porcentaje(porcentaje)

    def descontar_porcentaje_dialog(self):
        """Input dialog para ingresar porcentaje"""

        user_input = qtw.QInputDialog()

        porcentaje, ok = user_input.getDouble(self,
                                              'Porcentaje',
                                              'Porcentaje: ',
                                              qtw.QLineEdit.Normal,
                                              0, 100)
        if porcentaje and ok:
            self.descontar_porcentaje(porcentaje)

    def descontar_porcentaje(self, porcentaje):
        idxs = self.table.selectedIndexes()
        porcentaje = porcentaje / 100
        if idxs:
            msg = qtw.QMessageBox()
            msg.setText(f'¿Está seguro de que desea modificar {len(idxs)} elementos?')
            msg.setWindowTitle(' ')
            msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel)
            ret = msg.exec_()
            if ret == qtw.QMessageBox.Ok:
                # print('Accepted')
                for idx in idxs:
                    try:
                        row = self.filter_proxy_model.mapToSource(idx).row()
                        col = self.filter_proxy_model.mapToSource(idx).column()
                        idx = round(float(idx.data()))
                        nuevo_precio = idx - (idx * porcentaje)
                        self.model._data[row][col] = nuevo_precio
                        # self.statusBar().showMessage('Valores modificados correctamente.', 10000)
                    except Exception as e:
                        msg = 'Seleccione únicamente celdas que contengan números.'
                        self.display_msg(msg, icon=qtw.QMessageBox.Critical,
                                         informativeText=f'Elemento: {idx.data()}',
                                         windowTitle='Error')
                else:
                    msg.close()

    def sumar_porcentaje(self, porcentaje):
        idxs = self.table.selectedIndexes()
        porcentaje = porcentaje / 100
        if idxs:
            msg = qtw.QMessageBox()
            msg.setText(f'¿Está seguro de que desea modificar {len(idxs)} elementos?')
            msg.setWindowTitle(' ')
            msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel)
            ret = msg.exec_()
            if ret == qtw.QMessageBox.Ok:
                # print('Accepted')
                for idx in idxs:
                    try:
                        # Map to source hace que todo funcione bien con la tabla filtrada.
                        row = self.filter_proxy_model.mapToSource(idx).row()
                        col = self.filter_proxy_model.mapToSource(idx).column()
                        idx = round(float(idx.data()))
                        # print(row, col, idx)
                        nuevo_precio = idx + (idx * porcentaje)
                        # print(nuevo_precio)
                        self.model._data[row][col] = nuevo_precio
                        # self.statusBar().showMessage('Valores modificados correctamente.', 10000)
                    except Exception as e:
                        text = 'Seleccione únicamente celdas que contengan números.'
                        self.display_msg(text, icon=qtw.QMessageBox.Critical,
                                         informativeText=f'Elemento: {idx.data()}',
                                         windowTitle='Error')
                else:
                    msg.close()

    def display_msg(self, string, **kwargs):
        msg = qtw.QMessageBox()
        msg.setWindowIcon(QIcon('png_aya.ico'))
        msg.setText(string)
        for k, v in kwargs.items():
            setattr(msg, k, v)
        try:
            msg.setInformativeText(str(kwargs.get('informativeText', ' ')))
            msg.setIcon(kwargs.get('icon', None))
            msg.setWindowTitle(str(kwargs.get('windowTitle', ' ')))
        except Exception as e:
            print(e)
        msg.exec_()

class MainWindow(qtw.QWidget):

    settings = qtc.QSettings('Arte & Arquitectura', 'Gestor Arte & Arquitectura')
    start = time.perf_counter()
    presupuesto = pd.read_csv('database/DB/presupuestos_limpio.csv', sep=',')
    # productos = pd.read_csv('database/DB/productos.csv', sep=',')
    end = time.perf_counter()
    print(end - start)

    def __init__(self):

        super().__init__()
        start = time.perf_counter()
        self.setWindowTitle('Arte & Arquitectura')
        self.setWindowIcon(QIcon('png_aya.ico'))

        self.productos = None
        self.threadpool = qtc.QThreadPool()
        # self.cargar_data_productos()
        self.load_data_thread()

        self.setFixedWidth(1600)
        self.setFixedHeight(900)
        # self.resize(1000, 900)
        self.fecha = datetime.datetime.now().date().strftime('%d-%m-%Y')
        # setup barra de menu y sus botones
        self.menu = qtw.QMenuBar(objectName='menu')
        self.menu.addAction('Abrir tabla productos', self.abrir_tabla_productos)
        self.menu.addAction('Abrir tabla de presupuestos', self.abrir_tabla_presupuestos)
        self.menu.addAction('Cargar producto nuevo', self.cargar_producto)

        # setup de la status bar
        self.status_bar = qtw.QStatusBar()

        # Título y logo
        self.title = qtw.QLabel('Arte & Arquitectura', objectName='titulo')
        self.title.setAlignment(qtc.Qt.AlignTop)

        self.logo = QPixmap('png_aya_blanco.png')
        self.image = qtw.QLabel(self)
        scaled_pixmap = self.logo.scaled(130, 130, qtc.Qt.KeepAspectRatio)
        self.image.setPixmap(scaled_pixmap)
        self.image.setAlignment(qtc.Qt.AlignRight)

        # Crea lineedits y comboboxes
        self.crear_widgets()

        # Cargar los items a las comboboxes, luego los completers y luego el stylesheet
        # self.setup_comboboxes()
        # self.style_sheet_completers()

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
        self.total1 = qtw.QLineEdit(objectName='total1')
        self.total2 = qtw.QLineEdit(objectName='total2')
        self.total3 = qtw.QLineEdit(objectName='total3')
        self.total4 = qtw.QLineEdit(objectName='total4')
        self.total5 = qtw.QLineEdit(objectName='total5')
        self.total6 = qtw.QLineEdit(objectName='total6')
        self.total7 = qtw.QLineEdit(objectName='total7')
        self.total8 = qtw.QLineEdit(objectName='total8')

        # Totales
        self.label_p_unitario2 = qtw.QLabel('P. Unitario',
                                            objectName='preciounitariolabel')
        self.label_total2 = qtw.QLabel('Total',
                                       objectName='preciototallabel')
        self.punit = qtw.QLabel('0.00', objectName='preciounitario')
        self.total = qtw.QLabel('0.00', objectName='preciototal')

        # Otros
        self.otro1 = qtw.QLineEdit(objectName='otro1')
        self.otro2 = qtw.QLineEdit(objectName='otro2')
        self.otro3 = qtw.QLineEdit(objectName='otro3')

        self.p_otro1 = qtw.QLineEdit(objectName='p_otro1')
        self.p_otro2 = qtw.QLineEdit(objectName='p_otro2')
        self.p_otro3 = qtw.QLineEdit(objectName='p_otro3')

        # Botones
        self.btn_borrar = qtw.QPushButton('Borrar',
                                          objectName='botonborrar')
        self.btn_borrar.setToolTip('Limpiar todos los campos')
        self.btn_pdf = qtw.QPushButton(objectName='botonpdf')
        self.btn_pdf.setToolTip('Generar PDF para orden de trabajo o presupuesto')
        self.eliminar_presupuesto = qtw.QPushButton('')
        self.eliminar_presupuesto.setToolTip('Eliminar presupuesto actual de la base de datos')
        self.trabajo_completo = qtw.QPushButton(objectName='botoncompletado')
        self.trabajo_completo.setToolTip('Marcar el trabajo actual como completado')
        completado_icon = QIcon('checkmark.ico')
        eliminar_icon = QIcon('trash-icon.ico')
        pdf_icon = QIcon('pdf.ico')
        self.btn_pdf.setIcon(pdf_icon)
        self.eliminar_presupuesto.setIcon(eliminar_icon)
        self.trabajo_completo.setIcon(completado_icon)

        # Layout
        main_layout = qtw.QVBoxLayout()
        self.grid1 = qtw.QGridLayout(objectName='grid1')
        self.grid2 = qtw.QGridLayout()
        box1 = qtw.QGroupBox(' ')
        self.setLayout(main_layout)

        main_layout.setMenuBar(self.menu)

        # Adding grid1
        main_layout.addLayout(self.grid1)
        self._add_to_grid(self.grid1, [
            (self.title, 0, 0, 1, 2),
            (self.image, 0, 3, 1, 2),
            (qtw.QSpacerItem(10, 20), 1, 0),
            (qtw.QLabel('Presupuestos pendientes'), 2, 0),
            (self.presupuestos_pendientes, 2, 1),
            (qtw.QLabel('Clientes'), 3, 0),
            (self.clientes_combo, 3, 1),
            (qtw.QLabel('Trabajos (todos)'), 2, 3),
            (self.trabajos_todos, 2, 4),
            (qtw.QLabel('Trabajos (este año)'), 3, 3),
            (self.trabajos_año, 3, 4),
            (qtw.QSpacerItem(10, 20), 4, 0),
        ])

        # Adding grid2
        main_layout.addLayout(self.grid2)
        self._add_to_grid(self.grid2, [
            (qtw.QLabel('Cliente'), 1, 1),
            (self.cliente, 1, 2, 1, 2),
            (qtw.QLabel('Motivo'), 2, 1),
            (self.motivo, 2, 2, 2, 2),
            (qtw.QLabel('Cant.'), 1, 4),
            (self.cantidad, 2, 4, 1, 1),
            (qtw.QSpacerItem(10, 20), 3, 1),
            (qtw.QLabel('Fecha Recepción'), 4, 1),
            (self.fecha_rec, 4, 2),
            (qtw.QLabel('Fecha Entrega'), 5, 1),
            (self.fecha_entrega, 5, 2),
            (qtw.QLabel('Fecha Realización'), 4, 3),
            (self.fecha_realizacion, 5, 3),
            (qtw.QLabel('Med. Orig. cm.'), 1, 6, 2, 1),
            (self.med_orig_cm_ancho, 1, 7),
            (self.med_orig_cm_alto, 2, 7),
            (qtw.QLabel('pp. cm'), 1, 8),
            (self.pp_cm, 1, 9),
            (qtw.QLabel('var.'), 2, 8),
            (self.var, 2, 9),
            (qtw.QLabel('Med. Final cm.'), 4, 6, 2, 1),
            (self.med_final_cm_ancho, 4, 7),
            (self.med_final_cm_alto, 5, 7),
            (qtw.QLabel('Sup. m2:'), 4, 8),
            (self.sup_m2, 4, 9),
            (qtw.QLabel('Per. ml:'), 5, 8),
            (self.per_ml, 5, 9),
            (qtw.QSpacerItem(10, 20), 6, 1),
            (self.label_nombre, 7, 1),
            (self.combo1, 8, 1, 1, 4),
            (self.combo2, 9, 1, 1, 4),
            (self.combo3, 10, 1, 1, 4),
            (self.combo4, 11, 1, 1, 4),
            (self.combo5, 12, 1, 1, 4),
            (self.combo6, 13, 1, 1, 4),
            (self.combo7, 14, 1, 1, 4),
            (self.combo8, 15, 1, 1, 4),
            (self.label_stock, 7, 5),
            (self.stock1, 8, 5),
            (self.stock2, 9, 5),
            (self.stock3, 10, 5),
            (self.stock4, 11, 5),
            (self.stock5, 12, 5),
            (self.stock6, 13, 5),
            (self.stock7, 14, 5),
            (self.stock8, 15, 5),
            (self.label_p_unitario, 7, 6),
            (self.punitario1, 8, 6),
            (self.punitario2, 9, 6),
            (self.punitario3, 10, 6),
            (self.punitario4, 11, 6),
            (self.punitario5, 12, 6),
            (self.punitario6, 13, 6),
            (self.punitario7, 14, 6),
            (self.punitario8, 15, 6),
            (self.label_total, 7, 7),
            (self.total1, 8, 7),
            (self.total2, 9, 7),
            (self.total3, 10, 7),
            (self.total4, 11, 7),
            (self.total5, 12, 7),
            (self.total6, 13, 7),
            (self.total7, 14, 7),
            (self.total8, 15, 7),
            (qtw.QSpacerItem(10, 20), 16, 1),
            (self.otro1, 17, 1, 1, 5),
            (self.otro2, 18, 1, 1, 5),
            (self.otro3, 19, 1, 1, 5),
            (self.p_otro1, 17, 7),
            (self.p_otro2, 18, 7),
            (self.p_otro3, 19, 7),
            (self.label_p_unitario2, 7, 8, 1, 2),
            (self.punit, 9, 8, 2, 2),
            (self.label_total2, 7, 10, 1, 2),
            (self.total, 9, 10, 2, 2),
            (self.btn_borrar, 11, 9, 2, 1),
            (self.btn_pdf, 13, 8, 2, 1),
            (self.eliminar_presupuesto, 13, 9, 2, 1),
            (self.trabajo_completo, 13, 10, 2, 1),
        ])

        # Add spacers
        main_layout.addSpacerItem(qtw.QSpacerItem(10, 30))
        main_layout.addSpacerItem(qtw.QSpacerItem(10, 50))
        main_layout.addWidget(self.status_bar)

        end = time.perf_counter()
        total = end - start
        print(f'Widgets and layout: {total}')
        #### Combo-boxes ####
        ### Clientes
        start1 = time.perf_counter()

        # self.model = qtc.QStringListModel()
        self.completer_trabajos = qtw.QCompleter(
            self.presupuesto.loc[:, 'Motivo'], self
        )
        # self.completer_trabajos.setModel(self.model)
        # self.model.setStringList(self.presupuesto.loc[:, 'Motivo'].values)
        self.completer_trabajos.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_trabajos.setFilterMode(qtc.Qt.MatchContains)
        self.completer_clientes = qtw.QCompleter(
            sorted(self.presupuesto.loc[:, 'Cliente'].unique()), self
        )
        self.completer_clientes.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_clientes.setFilterMode(qtc.Qt.MatchContains)

        self.clientes_combo.addItem('')
        self.clientes_combo.addItems(
            sorted(self.presupuesto.loc[:, 'Cliente'].unique()))
        self.trabajos_todos.addItem('')
        self.trabajos_todos.addItems(
            sorted(self.presupuesto.loc[:, 'Motivo'])
        )
        self.trabajos_todos.setEditable(True)
        self.clientes_combo.setEditable(True)
        self.trabajos_todos.setCompleter(self.completer_trabajos)
        self.clientes_combo.setCompleter(self.completer_clientes)

        # Trabajos este año
        self.year = qtc.QDateTime().currentDateTime().date().year()
        year_subset = self.presupuesto['F_Realizacion'].apply(
            lambda x: x.split('/')[-1]
        )
        year_subset = [year for year in year_subset if year == self.year]
        self.trabajos_año.addItems(year_subset)

        # Presupuestos pendientes
        pendientes = self.presupuesto[self.presupuesto['Completado'] == 0]['Motivo']
        self.completer_pendientes = qtw.QCompleter(pendientes, self)
        self.completer_pendientes.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_pendientes.setFilterMode(qtc.Qt.MatchContains)
        self.presupuestos_pendientes.addItem('')
        self.presupuestos_pendientes.addItems(pendientes)
        self.presupuestos_pendientes.setEditable(True)
        self.presupuestos_pendientes.setCompleter(self.completer_pendientes)

        # Productos
        end1 = time.perf_counter()
        total1 = end1 - start1
        print(f'Combo-box lists and completers: {total1}')
        # Validators
        self.validator = QDoubleValidator()
        self.med_orig_cm_ancho.setValidator(self.validator)
        self.med_final_cm_alto.setValidator(self.validator)
        self.pp_cm.setValidator(self.validator)
        self.var.setValidator(self.validator)
        self.p_otro1.setValidator(self.validator)
        self.p_otro2.setValidator(self.validator)
        self.p_otro3.setValidator(self.validator)

        # Non-editable
        self.med_final_cm_ancho.setEnabled(False)
        self.med_final_cm_alto.setEnabled(False)
        self.sup_m2.setEnabled(False)
        self.per_ml.setEnabled(False)
        self.fecha_realizacion.setEnabled(False)

        self.stock1.setEnabled(False)
        self.stock2.setEnabled(False)
        self.stock3.setEnabled(False)
        self.stock4.setEnabled(False)
        self.stock5.setEnabled(False)
        self.stock6.setEnabled(False)
        self.stock7.setEnabled(False)
        self.stock8.setEnabled(False)

        self.punitario1.setEnabled(False)
        self.punitario2.setEnabled(False)
        self.punitario3.setEnabled(False)
        self.punitario4.setEnabled(False)
        self.punitario5.setEnabled(False)
        self.punitario6.setEnabled(False)
        self.punitario7.setEnabled(False)
        self.punitario8.setEnabled(False)

        self.total1.setEnabled(False)
        self.total2.setEnabled(False)
        self.total3.setEnabled(False)
        self.total4.setEnabled(False)
        self.total5.setEnabled(False)
        self.total6.setEnabled(False)
        self.total7.setEnabled(False)
        self.total8.setEnabled(False)


        ####Conexiones####
        # self.connect_comboboxes()

        # Borrar
        self.btn_borrar.clicked.connect(self.borrar_formulario)
        self.eliminar_presupuesto.clicked.connect(self.borrar_presupuesto_cargado)

        # Confirmar trabajo
        # self.btn_pdf.clicked.connect(self.cargar_venta)
        self.btn_pdf.clicked.connect(lambda: self.message(
            string='Presione OK para generar orden de trabajo. \n'
                   'Presione Guardar para guardar detalle de presupuesto',
            method=lambda: self.cargar_orden_trabajo(),
            windowTitle='Confirmación',
            icon=qtw.QMessageBox.Question))
        # Marcar trabajo como completo
        self.trabajo_completo.clicked.connect(self.completar_trabajo)

        # Medidas
        self.med_orig_cm_ancho.textChanged.connect(self.calculo_medidas)
        self.med_orig_cm_alto.textChanged.connect(self.calculo_medidas)
        self.pp_cm.textChanged.connect(self.calculo_medidas)
        self.var.textChanged.connect(self.calculo_medidas)

        # Otros
        for p in [self.p_otro1, self.p_otro2, self.p_otro3]:
            p.textChanged.connect(self.display_p_unitario)
            p.textChanged.connect(self.display_total)

        self.cantidad.textChanged.connect(self.display_total)

        # Motivo
        self.trabajos_todos.activated.connect(lambda: self.complete_from_work(
            string=self.trabajos_todos.currentText(), client=self.clientes_combo.currentText(),
            index=self.completer_trabajos.currentIndex().row()
        ))
        self.presupuestos_pendientes.activated.connect(
            lambda: self.complete_from_work(
                string=self.presupuestos_pendientes.currentText()
            )
        )
        self.clientes_combo.activated.connect(
            lambda: self.complete_from_cliente(
                string=self.clientes_combo.currentText()
            )
        )
        self.clientes_combo.textActivated.connect(
            self.restaurar_lista_trabajos)

        # stylesheet

        self.completer_clientes.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                      "selection-background-color: #FF9B99;"
                                                      "selection-color:solidblack;")
        self.completer_trabajos.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                      "selection-background-color: #FF9B99;"
                                                      "selection-color: solidblack;")
        self.completer_pendientes.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")

        self.status_bar.setStyleSheet("color:white; font-size: 13pt;")
        # Show
        self.show()

    def crear_widgets(self):
        """Crea e inicializa widgets."""
        self.presupuestos_pendientes = qtw.QComboBox(objectName='trabajos_pendientes')
        self.clientes_combo = qtw.QComboBox()
        self.trabajos_todos = qtw.QComboBox(objectName='combo_trabajos_todos')
        self.trabajos_año = qtw.QComboBox()

        self.cliente = qtw.QLineEdit(objectName='cliente')
        self.motivo = qtw.QTextEdit(objectName='motivo')
        self.cantidad = qtw.QLineEdit('1', objectName='cantidad')
        self.med_orig_cm_alto = qtw.QLineEdit(objectName='alto_original')
        self.med_orig_cm_ancho = qtw.QLineEdit(objectName='ancho_original')
        self.med_final_cm_alto = qtw.QLineEdit(objectName='alto_final')
        self.med_final_cm_ancho = qtw.QLineEdit(objectName='ancho_final')
        self.med_final_cm_ancho.setText('0')
        self.med_final_cm_alto.setText('0')
        self.pp_cm = qtw.QLineEdit(objectName='pp')
        self.var = qtw.QLineEdit(objectName='var')
        self.sup_m2 = qtw.QLineEdit()
        self.per_ml = qtw.QLineEdit()

        self.fecha_rec = qtw.QLineEdit(self.fecha, objectName='fecha_recepción')
        self.fecha_entrega = qtw.QLineEdit(objectName='fecha_entrega')
        self.fecha_realizacion = qtw.QLineEdit(objectName='fecha_realización')

        #### Detalle ####
        # Col 1
        self.label_nombre = qtw.QLabel('Nombre del producto')
        self.combo1 = qtw.QComboBox(objectName='item1')
        self.combo2 = qtw.QComboBox(objectName='item2')
        self.combo3 = qtw.QComboBox(objectName='item3')
        self.combo4 = qtw.QComboBox(objectName='item4')
        self.combo5 = qtw.QComboBox(objectName='item5')
        self.combo6 = qtw.QComboBox(objectName='item6')
        self.combo7 = qtw.QComboBox(objectName='item7')
        self.combo8 = qtw.QComboBox(objectName='item8')

        self.combo_boxes = [self.combo1, self.combo2, self.combo3, self.combo4, self.combo5, self.combo6, self.combo7,
                            self.combo8]

    def load_data_thread(self):
        """Cargar la data de productos en un thread aparte.
        Aumenta significativamente la velocidad de booteo"""
        worker = Worker(self.cargar_data_productos)
        worker.signals.result.connect(self.on_data_loaded)
        self.threadpool.start(worker)

    def on_data_loaded(self, productos):
        """Manejar los procesos luego de la carga de datos."""
        self.productos = productos
        self.setup_comboboxes()
        self.style_sheet_comboboxes()
        self.style_sheet_completers()
        self.connect_comboboxes()

        # Ubicar según necesidad inicializaciones adicionales o actualizaciones acá.

    def cargar_data_productos(self):
        """
        Cargar datos de productos de un archivo CSV.
        Se fija si el path está guardado en los settings; si no,
        insta al usuario a seleccionar el archivo.
        """
        # Revisa si el path de la base está en los valores de configuración
        if 'DB_Productos' in self.settings.allKeys():
            path = self.settings.value('DB_Productos')
        else:
            # Insta al usuario a elegir el archivo en los directorios
            path, _ = qtw.QFileDialog.getOpenFileName(
                self,
                'Abrir base de datos de productos',
                qtc.QDir.currentPath(),
                'CSV Files (*.csv);;All Files (*)'
            )
            # Guarda el path en la configuración
        if path:
            self.settings.setValue('DB_Productos', path)
            # Trata de cargar el archivo CSV
            try:
                self.productos = pd.read_csv(path, sep=',')
            except FileNotFoundError:
                qtw.QMessageBox.critical(self, 'Error', 'El archivo no se encontró. Verifique la ruta.')
                return None
            except pd.errors.EmptyDataError:
                qtw.QMessageBox.critical(self, 'Error', 'El archivo está vacío.')
                return None
            except Exception as e:
                qtw.QMessageBox.critical(self, 'Error', f'Error al cargar el archivo: {str(e)}')
                return None

            return self.productos

    def _add_to_grid(self, grid, items):
        """Helper function to add items to a grid layout."""
        for item in items:
            if isinstance(item[0], qtw.QSpacerItem):
                grid.addItem(item[0], item[1], item[2])
            else:
                if len(item) == 3:  # widget, row, column
                    grid.addWidget(item[0], item[1], item[2])
                elif len(item) == 4:  # widget, row, column, rowSpan
                    grid.addWidget(item[0], item[1], item[2], item[3])
                elif len(item) == 5:  # widget, row, column, rowSpan, columnSpan
                    grid.addWidget(item[0], item[1], item[2], item[3], item[4])

    def setup_comboboxes(self):
        # Extract valid items from the DataFrame once
        valid_items = self.productos['DenominaciónCompleta'].dropna().astype(str).unique()
        valid_items = [item for item in valid_items if item]  # Filter out empty strings

        # Store completers as attributes
        self.completers = []

        for combo_box in self.combo_boxes:
            completer = self.setup_combobox(combo_box, valid_items)
            self.completers.append(completer)  # Store each completer for later use

    def setup_combobox(self, combo_box, items):
        combo_box.clear()
        combo_box.addItem('')  # Placeholder
        combo_box.addItems(items)
        combo_box.setEditable(True)

        completer = qtw.QCompleter(items)
        completer.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        completer.setFilterMode(qtc.Qt.MatchContains)

        combo_box.setCompleter(completer)

        return completer

    def style_sheet_comboboxes(self):
        for combobox in self.combo_boxes:
            combobox.setStyleSheet('''QComboBox { 
                        font-size: 13pt;
                        color: black;''')

    def style_sheet_completers(self):
        for completer in self.completers:
            completer.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                       "selection-background-color: #7E9EC9;"
                                                       "selection-color: solidblack;")

    def connect_comboboxes(self):
        """Conecta las comboboxes de productos con los métodos necesarios."""
        for i in range(1, 9):
            combo = getattr(self, f'combo{i}')
            combo.activated.connect(lambda checked, c=combo: self.complete_products(string=c.currentText(),
                                                                                    idx=self.grid2.indexOf(c)))
            combo.lineEdit().textEdited.connect(lambda text, c=combo: self.borrar_precios(self.grid2.indexOf(c)))

    # Reporte pdf
    def getPath(self):
        path = None
        if 'PDF_Path' in self.settings.allKeys():
            # generate(dic, settings.value('PDF_Path'))
            path = self.settings.value('PDF_Path')
            if not os.path.isdir(path):  # Revisa si el path es un directorio válido
                qtw.QMessageBox.warning(self, 'Guarda loco', 'Dirección inválida. Elija otra.')
                path = None  # Reset del path para pedir otro

        # Si no se encuentra path válido, pide otro
        if path is None:
            path = qtw.QFileDialog.getExistingDirectory(
                self,
                'Guardar PDF',
                qtc.QDir.currentPath(),
                qtw.QFileDialog.ShowDirsOnly | qtw.QFileDialog.DontResolveSymlinks
            )
        # Si el path es válido, lo guarda
        if path:
            self.settings.setValue('PDF_Path', path)
            return path
        # Si no se selecciona nada return None
        else:
            qtw.QMessageBox.information(self, 'Info', 'No seleccionaste nada.')
            return None

            # Settings

    def closeEvent(self, event):
        """Método que se dispara al cerrar el programa."""
        self.settings.setValue('window size', self.size())

    # Completer initiator
    def completers_from_presupuesto(self):
        """Iniciar y actualizar completers desde la base de datos de presupuestos"""
        try:
            presupuesto = pd.read_csv(
                'database/DB/presupuestos_limpio.csv')
            # Instanciar completers
            self.completer_trabajos = self.crear_completer(presupuesto['Motivo'])
            self.completer_clientes = self.crear_completer(presupuesto['Cliente'])
            pendientes = presupuesto[presupuesto['Completado'] == 0]['Motivo']
            self.completer_pendientes = self.crear_completer(pendientes)
            # Setear los completers para cada combobox
            self.set_completers()
        except Exception as e:
            # Handle error in loading presupuesto data
            self.status_bar.showMessage(f'Error al cargar presupuestos: {str(e)}', 10000)

    def crear_completer(self, data):
        completer = qtw.QCompleter(data, self)
        completer.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        completer.setFilterMode(qtc.Qt.MatchContains)
        self.style_completer_popup(completer)
        return completer

    def set_completers(self):
        """Set completers to the respective combo boxes."""
        self.trabajos_todos.setCompleter(self.completer_trabajos)
        self.clientes_combo.setCompleter(self.completer_clientes)
        self.presupuestos_pendientes.setCompleter(self.completer_pendientes)

    def style_completer_popup(self, completer):
        """Apply styling to the completer popup."""
        completer.popup().setStyleSheet(
            "color: white; font-size: 13pt;"
            "selection-background-color: #FF9B99;"
            "selection-color: solidblack;"
        )

    # Display
    def message(self, string, method, **kwargs):
        """Función para display de diálogo para selección entre generar orden y guardar pdf."""
        msg = qtw.QMessageBox()
        msg.setWindowIcon(QIcon('png_aya.ico'))
        msg.setText(string)
        for k, v in kwargs.items():
            setattr(msg, k, v)
        try:
            msg.setInformativeText(str(kwargs.get('informativeText', ' ')))
            msg.setIcon(kwargs.get('icon', None))
            msg.setWindowTitle(str(kwargs.get('windowTitle', ' ')))
        except Exception as e:
            self.status_bar.showMessage('Error configurando las propiedades del mensaje.', 10000)
        msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel | qtw.QMessageBox.Save)
        ret = msg.exec_()

        if ret == qtw.QMessageBox.Ok:
            check = self.checkpoint_datos_esenciales()
            if check:
                try:
                    method.__call__()
                except Exception as e:
                    print(f"Error in method call: {str(e)}")  # Log the specific error
                    self.status_bar.showMessage('Error processing the request.', 10000)
        elif ret == qtw.QMessageBox.Save:
            # método para exportar PDF / imprimir presupuesto sin guardarlo
            check = self.checkpoint_datos_esenciales()
            if check:
                self.generar_presupuesto()
        else:
            msg.close()

    def warning_message(self, string):
        message = string
        msg = qtw.QMessageBox()
        msg.setText(message)
        msg.setIcon(qtw.QMessageBox.Warning)
        msg.setWindowTitle('Datos insuficientes')
        msg.exec_()

    # Form methods
    @qtc.pyqtSlot()
    def complete_products(self, string, idx):
        """completa los precios según el producto elegido y los cálculos según las medidas"""
        subset = self.productos[
            self.productos['DenominaciónCompleta'] == string]
        row, column, cols, rows = self.grid2.getItemPosition(idx)
        stock = self.grid2.itemAtPosition(row, 5).widget()
        p_unit = self.grid2.itemAtPosition(row, 6).widget()
        #total = self.grid2.itemAtPosition(row, 7).widget()
        if len(self.med_final_cm_ancho.text()) > 0 and len(self.med_final_cm_alto.text()) > 0:
            ancho = float(self.med_final_cm_ancho.text())
            alto = float(self.med_final_cm_alto.text())
            self.calculo_total(ancho, alto)
        try:
            stock.setText(str(subset.loc[:, 'Stock'].values[0]))
            p_unit.setText(str(subset.loc[:, 'PrecioUnidad'].values[0]))
        except Exception as e:
            pass

    @qtc.pyqtSlot()
    def restaurar_lista_trabajos(self):
        try:
            if not self.sender().currentText():
                self.trabajos_todos.clear()
                self.trabajos_todos.addItem(' ')
                self.trabajos_todos.addItems(
                    sorted(self.presupuesto.loc[:, 'Motivo']))
        except Exception as e:
            print(str(e))

    def complete_from_cliente(self, string):
        if len(string) != 0:
            try:
                self.borrar_formulario()
                self.clientes_combo.setCurrentText(string)
                subset_motivos = self.presupuesto[self.presupuesto['Cliente'] == string]['Motivo'].values
                self.trabajos_todos.clear()
                self.trabajos_todos.addItems(subset_motivos)
            except Exception as e:
                self.status_bar.showMessage('aaaaaaaaaaaaaaaaaaaaa', 10000)
        else:
            self.trabajos_todos.clear()
            self.trabajos_todos.addItem('')
            self.trabajos_todos.addItems(sorted(self.presupuesto.loc[:, 'Motivo']))
            self.borrar_formulario()

    # Revisar aquí. Puede estar el problema de la carga de presupuestos y también de cuanado se intenta borrarlos.
    def complete_from_work(self, string, client='', index=0):
        if string and not client:
            if self.sender().objectName() == 'trabajos_pendientes':
                self.borrar_formulario()
            try:
                # self.borrar_formulario()
                subset = self.presupuesto[
                    self.presupuesto['Motivo'] == string
                ]
                if len(subset) != 0:
                    if len(subset) == 1:
                        self.fecha_rec.setText(subset['F_Recepción'].values[0])
                        self.fecha_entrega.setText(subset['F_Entrega'].values[0])
                        self.fecha_realizacion.setText(subset['F_Realizacion'].values[0])
                        self.cliente.setText(subset['Cliente'].values[0])
                        self.motivo.setText(subset['Motivo'].values[0])
                        self.cantidad.setText(str(int(subset['Cant'].values[0])))
                        self.med_orig_cm_ancho.setText(str(subset['cto1'].values[0]))
                        self.med_orig_cm_alto.setText(str(subset['cto2'].values[0]))
                        self.var.setText(str(subset['ctvar'].values[0]))
                        self.pp_cm.setText(str(subset['ctpp'].values[0]))
                        self.total.setText(str(subset['Total_General'].values[0]))
                        self.punit.setText(str(float(self.total.text()) / float(self.cantidad.text())))
                    else:
                        self.borrar_formulario()
                    self.completar_precios(subset)
                    self.completar_productos_from_work(subset)
                    self.completar_otros_items(subset)
                    self.completar_otros_precios(subset)
            except Exception as e:
                print(e)
        elif string and client:
            self.borrar_formulario()
            self.clientes_combo.setCurrentText(client)
            subset = self.presupuesto[(self.presupuesto['Motivo'] == string) & (self.presupuesto['Cliente'] == client)]
            self.fecha_rec.setText(subset['F_Recepción'].values[0])
            self.fecha_entrega.setText(subset['F_Entrega'].values[0])
            self.fecha_realizacion.setText(subset['F_Realizacion'].values[0])
            self.cliente.setText(subset['Cliente'].values[0])
            self.motivo.setText(subset['Motivo'].values[0])
            self.cantidad.setText(str(int(subset['Cant'].values[0])))
            self.med_orig_cm_ancho.setText(str(float(subset['cto1'].values[0])))
            self.med_orig_cm_alto.setText(str(float(subset['cto2'].values[0])))
            self.var.setText(str(subset['ctvar'].values[0]))
            self.pp_cm.setText(str(subset['ctpp'].values[0]))
            self.total.setText(str(subset['Total_General'].values[0]))
            self.punit.setText(str(float(self.total.text()) / float(self.cantidad.text())))

            self.completar_precios(subset)
            self.completar_productos_from_work(subset)
            self.completar_otros_items(subset)
            self.completar_otros_precios(subset)

    def completar_productos_from_work(self, subset):
        productos = [col for col in subset.columns if col.startswith('CC')]
        item_row = 8
        for col in productos:
            producto_id = int(subset.loc[:, col].values[0])
            if producto_id != 0:
                item = self.productos[
                    self.productos['Contador'] == producto_id]['DenominaciónCompleta'].values[0]
                self.grid2.itemAtPosition(item_row, 1).widget().setCurrentText(item)
                item_row += 1

    def completar_precios(self, subset):
        """Esta función completa con los precios con los que se fijaron presupuestos pasados"""
        precios = [col for col in subset.columns if col.startswith('ctpreciouni')]

        item_row = 8
        for col in precios:
            precio = subset.loc[:, col].values[0]

            if precio != 0:
                print(col, precio)
                try:
                    self.grid2.itemAtPosition(item_row, 6).widget().setText(str(precio))
                    item_row += 1
                except Exception as e:
                    print(e)

    def completar_otros_items(self, subset):
        otros = subset[['ctotros', 'ctotros1', 'ctotros2']]
        item_row = 17
        for col in otros:
            item = subset.loc[:, col].values[0]
            if item != 'S/D':
                self.grid2.itemAtPosition(item_row, 1).widget().setText(item)
                item_row += 1

    def completar_otros_precios(self, subset):
        otros = subset[['cttotalotros', 'cttotalotros1', 'cttotalotros2']]
        item_row = 17
        for col in otros:
            precio = subset.loc[:, col].values[0]
            if precio != 0:
                self.grid2.itemAtPosition(item_row, 7).widget().setText(str(precio))
                item_row += 1

    def checker(self):
        """Checkear todos los campos antes de cargar la venta"""
        for i in range(self.grid2.count()):
            item = self.grid2.itemAt(i).widget()
            if isinstance(item, qtw.QLineEdit):
                if item.objectName().startswith('total') and len(item.text()) == 0:
                    item.setText('0')
                elif item.objectName().startswith('p_') and len(item.text()) == 0:
                    item.setText('0')
                elif item.objectName() == 'pp' and len(item.text()) == 0:
                    item.setText('0')
                elif item.objectName() == 'var' and len(item.text()) == 0:
                    item.setText('0')
                else:  # lineEdits de "otros"
                    if len(item.text()) == 0 and len(item.objectName()) != 0:
                        item.setText('S/D')

        self.cargar_venta()

    def checkpoint_datos_esenciales(self):
        """Revisa campos esenciales (Cliente, Motivo, Medidas, y que haya al menos un producto seleccionado
        antes de continuar con la venta o generación de PDF."""
        count = 0
        for cb in self.combo_boxes:
            line_edit = cb.lineEdit()
            if line_edit and line_edit.text().strip() == '':
                count += 1
        if count == 8:
            message = "Ningún producto seleccionado."
            self.warning_message(message)
        elif not self.cliente.text() or not self.motivo.toPlainText() or not self.med_orig_cm_alto.text() \
            or not self.med_orig_cm_ancho.text():
            message = "Campos esenciales vacíos. Revise el formulario."
            self.warning_message(message)
        else:
            return True

    def preparar_dic_datos(self):
        cto1 = self.med_orig_cm_ancho.text().replace(',', '.')
        cto2 = self.med_orig_cm_alto.text().replace(',', '.')
        ctpp = self.pp_cm.text().replace(',', '.')
        ctvar = self.var.text().replace(',', '.')

        # try:
        pedido = {'id': self.presupuesto['id'].max() + 1, 'F_Entrega': self.fecha_entrega.text(),
                  'F_Recepción': self.fecha_rec.text(),
                  'F_Realizacion': 'S/D',
                  'Cliente': self.cliente.text(), 'Motivo': self.motivo.toPlainText(),
                  'cto1': cto1, 'cto2': cto2, 'ctpp': ctpp,
                  'ctvar': ctvar, 'ctotros': self.otro1.text(),
                  'cttotalotros': self.p_otro1.text(),
                  'ctotros1': self.otro2.text(), 'cttotalotros1': self.p_otro2.text(),
                  'ctotros2': self.otro3.text(), 'cttotalotros2': self.p_otro3.text(),
                  'Total_General': self.total.text(), 'Cant': self.cantidad.text(),
                  'Completado': 0
                  }
        float_cols = ['cto1', 'cto2', 'ctpp', 'ctvar', 'cttotalotros', 'cttotalotros1',
                      'cttotalotros2', 'Total_General', 'Cant']
        text_cols = ['F_Entrega', 'F_Recepción', 'Cliente', 'Motivo', 'ctotros', 'ctotros1', 'ctotros2',
                     ]
        for col in float_cols:
            try:
                pedido[col] = float(pedido[col])
            except Exception as e:
                pedido[col] = 0
        for col in text_cols:
            try:
                if len(pedido[col]) == 0:
                    pedido[col] = 'S/D'
            except Exception as e:
                print(col, e)
        return pedido

    def generar_presupuesto(self):
        """Generar un detalle de trabajo en PDF sin cargar los datos al CSV de presupuestos"""
        try:
            pedido = self.preparar_dic_datos()
            count = 1
            col1 = 1  # columna de nombre
            col2 = 7  # columna de precios
            item_list = []
            for row in range(8, 16):
                producto = self.grid2.itemAtPosition(row, col1).widget().currentText()
                if len(producto) > 0:
                    precio = self.grid2.itemAtPosition(row, col2).widget().text()
                    p_unit = self.grid2.itemAtPosition(row, 6).widget().text()
                    # get item id
                    item_name = self.productos[
                        self.productos[
                            'DenominaciónCompleta'] == producto][
                        'DenominaciónCompleta'].values[0]
                    item_id = self.productos[
                        self.productos[
                            'DenominaciónCompleta'] == producto]['Contador'].values[0]
                    pedido['CCProducto' + str(count)] = item_id
                    pedido['ctpreciouni' + str(count)] = '%.2f' % float(precio)
                    pedido['p_unitario' + str(count)] = '%.2f' % float(p_unit)
                    item_list.append(item_name)
                    count += 1
                else:
                    item_id = 0
                    precio = 0
                    pedido['CCProducto' + str(count)] = item_id
                    pedido['ctpreciouni' + str(count)] = precio
                    pedido['p_unitario' + str(count)] = p_unit
                    count += 1
            pedido['Lista_Items'] = item_list
            pedido['sup'] = self.sup_m2.text() or ''
            pedido['per'] = self.per_ml.text() or ''
            pedido['med_alto_final'] = self.med_final_cm_alto.text() or ''
            pedido['med_ancho_final'] = self.med_final_cm_ancho.text() or ''
            path = self.getPath()
            if path:
                nombre_pdf = generate(pedido, path)
                self.status_bar.showMessage('PRESUPUESTO GENERADO.', 10000)
                try:
                    self.printPDF(nombre_pdf)
                except Exception as e:
                    print(e)
        except Exception as e:
            self.handle_pdf_path_error(e, pedido)
        self.borrar_formulario()

    def cargar_orden_trabajo(self):
        """Cargar toda la información al CSV de presupuestos y generar orden de trabajo en PDF"""
        try:
            pedido = self.preparar_dic_datos()
            count = 1
            col1 = 1  # columna de nombre
            col2 = 7   # columna de precios
            item_list = []  # lista de items para cargar
            for row in range(8, 16):                 # extrae items por combobox
                producto = self.grid2.itemAtPosition(row, col1).widget().currentText()
                if producto:
                    precio = self.grid2.itemAtPosition(row, col2).widget().text()
                    p_unit = self.grid2.itemAtPosition(row, 6).widget().text()
                    # get item id
                    try:
                        item_name, item_id = self.get_item_details(producto)
                    except Exception as e:
                        print(f'Error getting item details: {str(e)}')
                        item_name, item_id = '', 0
                    pedido['CCProducto' + str(count)] = item_id
                    pedido['ctpreciouni' + str(count)] = '%.2f' % float(precio)
                    pedido['p_unitario' + str(count)] = '%.2f' % float(p_unit)
                    item_list.append(item_name)
                    count += 1
                else:
                    p_unit = 0
                    self.add_empty_item(pedido, count, p_unit)
                    count += 1
            self.guardar_presupuesto(pedido)     # Guarda la nueva venta en el csv de presupuesto
            self.completers_from_presupuesto()   # Resetea los combobox de presupuestos
            self.trabajos_todos.addItem(pedido['Motivo'])
            self.clientes_combo.addItem(pedido['Cliente'])
            self.presupuestos_pendientes.addItem(pedido['Motivo'])
            pedido['Lista_Items'] = item_list
            pedido['sup'] = self.sup_m2.text() or ''
            pedido['per'] = self.per_ml.text() or ''
            pedido['med_alto_final'] = self.med_final_cm_alto.text() or ''
            pedido['med_ancho_final'] = self.med_final_cm_ancho.text() or ''

            path = self.getPath()            # Método para obtener el directorio de guardado
            if path:
                nombre_pdf = orden_trabajo(pedido, path)
                self.status_bar.showMessage('PDF DE ORDEN GUARDADO CORRECTAMENTE', 10000)
                try:
                    self.printPDF(nombre_pdf)
                except Exception as e:
                    print(e)
            else:
                raise ValueError('No se seleccionó una dirección válida para el PDF.')
        except Exception as e:
            self.handle_pdf_path_error(e, pedido)

        self.borrar_formulario()

    def printPDF_deprecated(self, pdf_path):
        if not os.path.exists(pdf_path):
            qtw.QMessageBox.warning(self, 'Error', 'El archivo PDF no existe.')
            return

        printer = qtw.QPrinter()
        printer.setPageSize(qtw.QPrinter.A4)
        printer.setOrientation(qtw.QPrinter.Landscape)

        # Open the PDF for printing
        painter = qtg.QPainter(printer)
        painter.setRenderHint(qtg.QPainter.Antialiasing)

        # Load the PDF and print it
        document = qtw.QPdfDocument()
        document.load(pdf_path)
        document.render(painter)

        painter.end()
        qtw.QMessageBox.information(self, 'Info', 'PDF enviado a la impresora.')

    def printPDF_poppler(self, pdf_path):
        if not os.path.exists(pdf_path):
            qtw.QMessageBox.warning(self, 'Error', 'El archivo PDF no existe.')
            return
        try:
            images = convert_from_path(pdf_path)
            if not images:
                print("No images were created from the PDF.")
                return

            printer = QPrinter(QPrinter.HighResolution)

            for image in images:
                painter = QPainter(printer)
                painter.drawImage(0, 0, QImage(image))
                painter.end()

            qtw.QMessageBox.information(self, 'Info', 'PDF enviado a la impresora.')

        except Exception as e:
            qtw.QMessageBox.critical(self, 'Error', str(e))

    def printPDF(self, pdf_path):
        """Abre el PDF generado en el visor de PDFs default del sistema para imprimir rápidamente."""
        if not os.path.exists(pdf_path):
            qtw.QMessageBox.warning(self, 'Error', 'El archivo PDF no existe.')
            return
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen([pdf_path], shell=True)  # Opens with default viewer on Windows

            qtw.QMessageBox.information(self, 'Info', 'PDF enviado a la impresora.')
        except Exception as e:
            qtw.QMessageBox.critical(self, 'Error', f"Error opening PDF: {str(e)}")

    def get_item_details(self, producto):
        """Extraer los detalles según el nombre del item.
        Returns: Nombre del Item; Id numérico, alias Contador en la base de datos."""
        item_name = \
        self.productos.loc[self.productos['DenominaciónCompleta'] == producto, 'DenominaciónCompleta'].values[0]
        item_id = self.productos.loc[self.productos['DenominaciónCompleta'] == producto, 'Contador'].values[0]
        return item_name, item_id

    def add_empty_item(self, pedido, count, p_unit):
        """Añade un item vacío al diccionario."""
        pedido[f'CCProducto{count}'] = 0
        pedido[f'ctpreciouni{count}'] = 0
        pedido[f'p_unitario{count}'] = p_unit

    def guardar_presupuesto(self, pedido):
        """Añade la orden de trabajo (presupuesto) al CSV de presupuestos."""
        dict_for_df = {key: value for key, value in pedido.items() if 'p_unitario' not in key}
        new_df = pd.DataFrame([dict_for_df])
        self.presupuesto = pd.concat([self.presupuesto, new_df], ignore_index=True)
        self.presupuesto.to_csv('database/DB/presupuestos_limpio.csv', index=False)
        # self.status_bar.showMessage('')

    def handle_pdf_path_error(self, error, pedido):
        """Manejo de errores de directorios para guardar los PDFs."""
        self.status_bar.showMessage('No se encontró el directorio.', 10000)
        path = self.getPath()  # Attempt to get a valid path
        if path:
            self.settings.setValue('PDF_Path', path)
            orden_trabajo(pedido, path)
            self.status_bar.showMessage('PDF de orden generado.', 10000)
        else:
            self.status_bar.showMessage('Dirección no válida para guardar PDF.', 10000)

    # Revisar
    @qtc.pyqtSlot()
    def completar_trabajo(self):
        """Marca un trabajo existente como completado."""
        try:
            combobox_index = self.presupuestos_pendientes.currentIndex()
            cliente = self.cliente.text()
            motivo = self.motivo.toPlainText()

            if len(cliente) > 0 and len(motivo) > 0:
                fecha = qtc.QDateTime.currentDateTime().toString('dd/MM/yyyy')
                index = self.presupuesto[
                    (self.presupuesto['Cliente'] == cliente) & (self.presupuesto['Motivo'] == motivo)].index[0]

                # self.presupuesto.drop(index, axis='index', inplace=True)
                completion_state = self.presupuesto.iloc[index, -1]
                if completion_state == 0:
                    self.presupuesto.iloc[index, -1] = 1
                    self.presupuesto.iloc[index, 3] = fecha
                    # Borrar esta línea luego de implementar guardado
                    self.presupuesto.to_csv('database/DB/presupuestos_limpio.csv', index=False)
                    self.status_bar.showMessage(
                        f'Trabajo de {cliente} con motivo: "{motivo}" completado el día {fecha}',
                        15000)
                    self.presupuestos_pendientes.removeItem(combobox_index)
                    self.borrar_formulario()
        except Exception as e:
            pass

    @qtc.pyqtSlot()
    def borrar_formulario(self):
        """Borra todos los campos de la ventana principal."""
        self.desconectar_textedits_medidas()
        for i in range(self.grid1.count()):
            item = self.grid1.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    if isinstance(widget, qtw.QComboBox):
                        widget.clearEditText()

        # print('Primer for loop terminado.')
        # print(self.grid2.count())
        for i in range(self.grid2.count()):
            try:
                item = self.grid2.itemAt(i)
                # print(f'Grabbed item')
                if item is not None:
                    widget = item.widget()
                    # print(f'Grabbed widget at index {i}: type{widget}')
                    if widget is None:
                        # print(f'No widget found for item at index {i}')
                        continue

                    if isinstance(widget, qtw.QComboBox):
                        print(
                            f'Widget {widget.objectName()} - '
                            f'Enabled: {widget.isEnabled()},'
                            f' Visible: {widget.isVisible()}')

                        widget.clearEditText()
                        print(f'Widget {widget.objectName()} cleared')
                    elif isinstance(widget, (qtw.QLineEdit, qtw.QTextEdit)):
                        print(
                            f'Widget {widget.objectName()} - '
                            f'Enabled: {widget.isEnabled()},'
                            f' Visible: {widget.isVisible()}')
                        try:
                            widget.clear()
                            # print(f'Widget {widget.objectName()} cleared')
                        except Exception as e:
                            print(e)
            except Exception as e:
                print(f'A ver qué te pasa: {e}')
        self.reconectar_textedits_medidas()
        # print('Segundo for loop terminado.')

        self.med_final_cm_ancho.setText('0')        # Setea valores por defecto
        self.med_final_cm_alto.setText('0')         # ! Setear fecha
        self.cantidad.setText('1')
        self.fecha_rec.setText(self.fecha)
        # print('Campos rellenados')
        # self.display_total()
        print('Display total hecho')
        if isinstance(self.sender(), qtw.QPushButton):
            # restaura lista original de trabajos
            # print('Restaurando listas')
            self.trabajos_todos.clear()
            self.trabajos_todos.addItem('')
            self.trabajos_todos.addItems(sorted(self.presupuesto.loc[:, 'Motivo']))
            # print('Listas restauradas')

    def borrar_presupuesto_cargado(self):
        """Borra el presupuesto que se ha cargado desde los comboboxes de la base de datos de presupuestos"""
        print('Borrando')
        try:
            cliente = self.cliente.text()
            motivo = self.motivo.toPlainText()
            if len(cliente) > 0 and len(motivo) > 0:
                index = self.presupuesto[
                    (self.presupuesto['Cliente'] == cliente) & (self.presupuesto['Motivo'] == motivo)].index[0]
                msg = qtw.QMessageBox()
                msg.setText(
                    f'Está seguro de que desea borrar el trabajo de {cliente} con motivo: {motivo}?')
                msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel)
                ret = msg.exec_()
                if ret == qtw.QMessageBox.Ok:
                    try:
                        print('Está entre esto...')
                        self.presupuesto.drop(index, axis='index', inplace=True)
                        self.presupuesto.to_csv('database/DB/presupuestos_limpio.csv', index=False)
                        print('...y esto?')
                        self.status_bar.showMessage(
                            f'Se eliminó el trabajo de {cliente} con motivo "{motivo}".', 15000)
                        self.borrar_formulario()
                        self.completers_from_presupuesto()
                    except IndexError as e:
                        print(f'Index Error: {e} ')
                else:
                    msg.close()
        except Exception as e:
            self.status_bar.showMessage('No, cht.')

    # Signal handling
    def desconectar_textedits_medidas(self):
        self.med_orig_cm_ancho.textChanged.disconnect()
        self.med_orig_cm_alto.textChanged.disconnect()
        self.pp_cm.textChanged.disconnect()
        self.var.textChanged.disconnect()

    def reconectar_textedits_medidas(self):
        self.med_orig_cm_ancho.textChanged.connect(self.calculo_medidas)
        self.med_orig_cm_alto.textChanged.connect(self.calculo_medidas)
        self.pp_cm.textChanged.connect(self.calculo_medidas)
        self.var.textChanged.connect(self.calculo_medidas)

    # Cálculos
    # Revisar si se puede mejorar.
    @qtc.pyqtSlot()
    def calculo_medidas(self):
        # medidas originales
        try:
            ancho = self.med_orig_cm_ancho.text().replace(',', '.')
            alto = self.med_orig_cm_alto.text().replace(',', '.')
            pp = self.pp_cm.text().replace(',', '.')
            var = self.var.text().replace(',', '.')
            lst = [ancho, alto, pp, var]
            for i in range(len(lst)):
                if len(lst[i]) == 0:
                    lst[i] = 0
                else:
                    try:
                        lst[i] = float(lst[i])
                    except Exception as e:
                        lst[i] = 0
                        print(f'Conversion error for {lst[i]}: {e}')

            final_ancho = lst[0] + (lst[2] * 2) + (lst[3] * 2)
            final_alto = lst[1] + (lst[2] * 2) + (lst[3] * 2)
            sup_m2 = final_ancho / 100 * final_alto / 100
            per_ml = (final_ancho * 2 + final_alto * 2) / 100

            sup_m2 = '%.2f' % sup_m2
            per_ml = '%.2f' % per_ml
            self.med_final_cm_ancho.setText(str(final_ancho))
            self.med_final_cm_alto.setText(str(final_alto))
            self.sup_m2.setText(str(sup_m2))
            self.per_ml.setText(str(per_ml))

            self.calculo_total(final_ancho, final_alto)
        except Exception as e:
            print(f'Herein lies {e}?')

    def calculo_total(self, ancho, alto):
        """Calcula el total unitario para cada item"""
        col = 6
        p_total = 0
        # si ya hay items elegidos:
        for row in range(8, 16):
            widget = self.grid2.itemAtPosition(row, col).widget()
            if len(widget.text()) > 0:
                # agarrar identificador de item y hacer cálculo según tipo en (row, 0)
                # varilla - m; vidrio, espejo, chapadur y  pp - sup.; pintura y patina - m y sup.
                item_id = self.grid2.itemAtPosition(row, 1).widget().lineEdit().text()[-1]
                if item_id == 'S':
                    if len(self.sup_m2.text()) != 0:
                        p_total = float(widget.text()) * float(self.sup_m2.text())
                        p_total = '%.2f' % p_total
                elif item_id == 'L':
                    if len(self.per_ml.text()) != 0:
                        p_total = float(widget.text()) * float(self.per_ml.text())
                        p_total = '%.2f' % p_total
                elif item_id == 'P':
                    alto = self.med_final_cm_alto.text()
                    ancho = self.med_final_cm_ancho.text()
                    if len(alto) != 0 and len(ancho) != 0:
                        highest = max(float(alto), float(ancho))
                        p_total = float(widget.text()) * (highest / 100)
                        p_total = '%.2f' % p_total
                elif item_id == 'U':
                    p_total = widget.text()
                else:
                    por_m2 = float(widget.text())
                    metros2 = (ancho / 100) * (alto / 100)
                    p_total = por_m2 * metros2
                    p_total = '%.2f' % p_total
                self.grid2.itemAtPosition(row, 7).widget().setText(str(p_total))
        self.display_total()
        self.display_p_unitario()

    # Display
    @qtc.pyqtSlot()
    def borrar_precios(self, idx):
        if not self.sender().text():
            try:
                row, _, _, _ = self.grid2.getItemPosition(idx)
                for column in range(5, 8):
                    widget = self.grid2.itemAtPosition(row, column).widget()
                    if widget:
                        widget.clear()
                self.display_total()
            except IndexError as e:
                print(f'Index Error: {e}')
            except Exception as e:
                print(f'Error inesperado: {e}')

    def display_total(self):
        """Muestra el total en la QLabel correspondiente"""
        cantidad = self.cantidad.text() or '0'  # Default to '0' if empty
        cantidad = int(cantidad) if cantidad.isdigit() else 0

        total_final = sum(
            float(self.grid2.itemAtPosition(row, 7).widget().text() or 0)
            for row in range(8, 20)
            if row != 16 and isinstance(self.grid2.itemAtPosition(row, 7).widget(), qtw.QLineEdit)
        )

        total_final *= cantidad
        self.total.setText(f'{total_final:.2f}')

    def display_p_unitario(self):
        """Muestra el precio unitario en la QLabel correspondiente"""
        total_unitario = 0
        for row in range(8, 20):
            if row != 16:
                item = self.grid2.itemAtPosition(row, 7).widget()
                if isinstance(item, qtw.QLineEdit):
                    text = item.text()
                    if len(text) > 0:
                        total_unitario += float(text)
        total_unitario = '%.2f' % total_unitario
        self.punit.setText(str(total_unitario))

    # Funciones de la barra del menú
    def abrir_tabla_presupuestos(self):
        self.tabla = Tabla('database/DB/presupuestos_limpio.csv')
        self.tabla.exec_()

    def abrir_tabla_productos(self):
        self.tabla = Tabla('database/DB/productos.csv')
        self.tabla.exec_()

    def cargar_producto(self):
        self.ventana_carga = CargarStock(self.productos)
        try:
            self.ventana_carga.exec_()
        except Exception as e:
            print(e)
        self.load_data_thread()


stylesheet = '''
#titulo {
color: #D2F1D0;
font: Italic;
font-size: 32pt;
font-family: Montserrat;
}
QWidget {background-color: #0B1119;}

QLabel {
font-size: 15pt;
font-family: Montserrat;
font: SemiBold;
color: #E1F6E0;
}
#preciounitario {
color: #0B1119 ;
border: 3px solid gray;
background-color: #C1D7D2;
border-style:outset;
border-width:3px;
border-color:#D2F1D0;
font-size: 19pt;
font-family: Montserrat;
font: SemiBold;

}
#preciototal {
color: #0B1119 ;
border: 3px solid gray;
background-color: #C1D7D2;
border-style:outset;
border-width:3px;
border-color:#F4F4ED;
font-size: 19pt;
font-family: Montserrat;
font: SemiBold;
}
QTextEdit {
font-size: 14pt;
font-family: Montserrat;
font: Medium;
border: 1px solid black;
background-color: #F4F4ED;   
selection-background-color: #7E9EC9;
selection-color: solidblack; 
}
QLineEdit {
    font-size: 14pt;
    font-family: Montserrat;
    font: Medium; 
    border: 1px solid black;
    background-color: #F4F4ED;   
    selection-background-color: #7E9EC9;
    selection-color: solidblack; 
}
QLineEdit:!enabled {
background-color: #C1D7D2;
color: #1D1E2C;
}
QComboBox {
subcontrol-origin: padding;
font-size: 14pt;
font-family: Montserrat;
font: Medium;
background-color: #F4F4ED;
color: black;
selection-background-color: #7E9EC9;
selection-color: solidblack;
border-style: solid;
border-radius: 5px;
}
QComboBox QLineEdit {
font-size: 14px;
font-family: Montserrat;
font: Medium;
}
QComboBox:hover {
border: 1px #7E9EC9;
}
QComboBox QAbstractItemView {
color: #F4F4ED;
}
QPushButton {
font-size: 15pt;
padding: 5px;
color: #F3E5CE;
background: #0B1119;
}
QPushButton:hover {background: #E1F6E0; color: #0B1119;}
#menu {spacing: 3px; font-size: 11pt; color: #E1F6E0;}
#menu::item {padding: 1px 4px; background: transparent; border-radius: 6px;}
#menu::item:selected {background: #E1F6E0; color: #0B1119}

'''

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    app.setStyleSheet(stylesheet)
    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = MainWindow()
    end = time.perf_counter()
    total = end - start

    sys.exit(app.exec())
