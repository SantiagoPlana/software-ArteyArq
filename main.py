import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5.QtGui import QPixmap, QDoubleValidator, QIcon
import pandas as pd
import csv
import time
import traceback
from pdf import generate, orden_trabajo

start = time.perf_counter()


class Signals(qtc.QObject):

    finished = qtc.pyqtSignal()
    error = qtc.pyqtSignal(tuple)
    result = qtc.pyqtSignal(object)


class Worker(qtc.QRunnable):

    def __init__(self, fn, *args, **kwargs):
        
        super(Worker, self).__init__()
        print('initiated')
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Signals()

    @qtc.pyqtSlot()
    def run(self):
        """Inicializa la función"""
        print('running')
        print(self.args, self.kwargs)
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
            print(fh)
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
        self.table.setStyleSheet('alternate-background-color: lightgray;  background-color: white;'
                                 'font-size: 12pt; selection-background-color: #FF9B99; ')
        self.menubar.setStyleSheet('spacing: 3px; font-size: 10pt; color: #F3E5CE;')
        self.menu_archivo.setStyleSheet('selection-background-color: #FF9B99; color: white; '
                                        'font-size: 10pt;')
        self.menu_editar.setStyleSheet('selection-background-color: #FF9B99; color: white; '
                                        'font-size: 10pt;')


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
        print(selected_proxy)
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
    productos = pd.read_csv('database/DB/productos.csv', sep=',')
    end = time.perf_counter()
    print(end - start)

    def __init__(self):

        super().__init__()
        start = time.perf_counter()
        self.setWindowTitle('Arte & Arquitectura')
        self.setWindowIcon(QIcon('png_aya.ico'))
        # self.showFullScreen()

        # self.center()
        #try:
        #    self.resize(self.settings.value('window size'))
        #except:
        self.setFixedWidth(1600)
        #self.resize(900, 700)

        self.menu = qtw.QMenuBar(objectName='menu')
        # self.menu.addAction('Guardar cambios')
        self.menu.addAction('Abrir tabla productos', self.abrir_tabla_productos)
        self.menu.addAction('Abrir tabla de presupuestos', self.abrir_tabla_presupuestos)

        self.status_bar = qtw.QStatusBar()

        self.threadpool = qtc.QThreadPool()

        self.title = qtw.QLabel('Presupuesto', objectName='titulo')
        self.title.setAlignment(qtc.Qt.AlignTop)
        # Logo
        self.logo = QPixmap('png_aya.png')
        self.image = qtw.QLabel(self)
        scaled_pixmap = self.logo.scaled(120, 120, qtc.Qt.KeepAspectRatio)
        self.image.setPixmap(scaled_pixmap)
        self.image.setAlignment(qtc.Qt.AlignRight)

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

        self.fecha_rec = qtw.QLineEdit(objectName='fecha_recepción')
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
        self.btn_pdf = qtw.QPushButton(objectName='botonpdf')
        self.eliminar_presupuesto = qtw.QPushButton('')
        self.trabajo_completo = qtw.QPushButton(objectName='botoncompletado')
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

        # main_layout.addWidget(self.menu)
        main_layout.setMenuBar(self.menu)
        # main_layout.addWidget(self.bar)
        main_layout.addLayout(self.grid1)
        self.grid1.addWidget(self.title, 0, 0, 1, 2)
        self.grid1.addWidget(self.image, 0, 3, 1, 2)

        self.grid1.addItem(qtw.QSpacerItem(10, 20), 1, 0)
        self.grid1.addWidget(qtw.QLabel('Presupuestos pendientes'), 2, 0)
        self.grid1.addWidget(self.presupuestos_pendientes, 2, 1)
        self.grid1.addWidget(qtw.QLabel('Clientes'), 3, 0)
        self.grid1.addWidget(self.clientes_combo, 3, 1)
        self.grid1.addWidget(qtw.QLabel('Trabajos (todos)'), 2, 3)
        self.grid1.addWidget(self.trabajos_todos, 2, 4)
        self.grid1.addWidget(qtw.QLabel('Trabajos (este año)'), 3, 3)
        self.grid1.addWidget(self.trabajos_año, 3, 4)

        # main_layout.addLayout(qtw.QSpacerItem(1, 1), 4, 1, 1, 6)
        self.grid2.addWidget(qtw.QLabel('Cliente'), 1, 1)
        self.grid2.addWidget(self.cliente, 1, 2, 1, 2)
        self.grid2.addWidget(qtw.QLabel('Motivo'), 2, 1)
        self.grid2.addWidget(self.motivo, 2, 2, 2, 2)
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
        self.grid2.addWidget(self.btn_borrar, 11, 9, 2, 1)
        self.grid2.addWidget(self.btn_pdf, 13, 8, 2, 1)
        self.grid2.addWidget(self.eliminar_presupuesto, 13, 9, 2, 1)
        self.grid2.addWidget(self.trabajo_completo, 13, 10, 2, 1)

        main_layout.addSpacerItem(qtw.QSpacerItem(10, 30))
        main_layout.addLayout(self.grid2)
        main_layout.addSpacerItem(qtw.QSpacerItem(10, 50))
        main_layout.addWidget(self.status_bar)
        #self.status_bar.showMessage('HEEEEEEEEEEEY', 20000)

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
        self.combo1.addItem('')
        self.combo1.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
        self.combo2.addItem('')
        self.combo2.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
        self.combo3.addItem('')
        self.combo3.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
        self.combo4.addItem('')
        self.combo4.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
        self.combo5.addItem('')
        self.combo5.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
        self.combo6.addItem('')
        self.combo6.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
        self.combo7.addItem('')
        self.combo7.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
        self.combo8.addItem('')
        self.combo8.addItems(
            self.productos.loc[:, 'DenominaciónCompleta'])
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
        # Borrar lineedits de precios y stock cuando se borra el producto
        self.combo1.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo1)))
        self.combo2.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo2)))
        self.combo3.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo3)))
        self.combo4.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo4)))
        self.combo5.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo5)))
        self.combo6.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo6)))
        self.combo7.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo7)))
        self.combo8.lineEdit().textEdited.connect(lambda:
                                                  self.borrar_precios(self.grid2.indexOf(self.combo8)))

        # Borrar
        self.btn_borrar.clicked.connect(self.borrar_formulario)
        self.eliminar_presupuesto.clicked.connect(self.borrar_presupuesto_cargado)

        # Confirmar trabajo
        # self.btn_pdf.clicked.connect(self.cargar_venta)
        self.btn_pdf.clicked.connect(lambda: self.message(
            string='Presione OK para cargar como venta. \n'
                   'Presione Guardar para guardar detalle de presupuesto',
            method=lambda: self.cargar_venta(),
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
        self.p_otro1.textChanged.connect(self.display_p_unitario)
        self.p_otro2.textChanged.connect(self.display_p_unitario)
        self.p_otro3.textChanged.connect(self.display_p_unitario)
        self.p_otro1.textChanged.connect(self.display_total)
        self.p_otro2.textChanged.connect(self.display_total)
        self.p_otro3.textChanged.connect(self.display_total)

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

        self.completer_productos.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                       "selection-background-color: #FF9B99;"
                                                       "selection-color: solidblack;")
        self.completer_productos2.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")
        self.completer_productos3.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;"
                                                        )
        self.completer_productos4.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")
        self.completer_productos5.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")
        self.completer_productos6.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")
        self.completer_productos7.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")
        self.completer_productos8.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                        "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")
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

    # Reporte pdf
    def getPath(self):
        settings = qtc.QSettings('Arte & Arquitectura', 'Gestor Arte & Arquitectura')
        if 'PDF_Path' in settings.allKeys():
            # generate(dic, settings.value('PDF_Path'))
            path = settings.value('PDF_Path')
            print(path)
        else:
            path = qtw.QFileDialog.getExistingDirectory(self,
                                                        'Guardar PDF',
                                                        qtc.QDir.currentPath(),
                                                        qtw.QFileDialog.ShowDirsOnly |
                                                        qtw.QFileDialog.DontResolveSymlinks)
            settings.setValue('PDF_Path', path)
        return path

    # Settings
    def closeEvent(self, event):
        """Método que se dispara al cerrar el programa."""
        self.settings.setValue('window size', self.size())

    # Completer initiator
    def completers_from_presupuesto(self):
        """Iniciar y actualizar completers desde la base de datos de presupuestos"""
        # database
        presupuesto = pd.read_csv(
            'database/DB/presupuestos_limpio.csv')
        # Instanciar completers
        self.completer_trabajos = qtw.QCompleter(
            presupuesto.loc[:, 'Motivo'], self
        )
        self.completer_clientes = qtw.QCompleter(
            presupuesto.loc[:, 'Cliente'], self
        )
        pendientes = presupuesto[presupuesto['Completado'] == 0]['Motivo']

        self.completer_pendientes = qtw.QCompleter(pendientes, self)
        # Propiedades
        self.completer_trabajos.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_trabajos.setFilterMode(qtc.Qt.MatchContains)
        self.completer_clientes.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_clientes.setFilterMode(qtc.Qt.MatchContains)
        self.completer_pendientes.setCaseSensitivity(qtc.Qt.CaseInsensitive)
        self.completer_pendientes.setFilterMode(qtc.Qt.MatchContains)
        # set
        self.trabajos_todos.setCompleter(self.completer_trabajos)
        self.clientes_combo.setCompleter(self.completer_clientes)
        self.presupuestos_pendientes.setCompleter(self.completer_pendientes)
        # print('Set')
        self.completer_clientes.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                      "selection-background-color: #FF9B99;"
                                                        "selection-color: solidblack;")
        self.completer_trabajos.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                      "selection-background-color: #FF9B99;"
                                                      "selection-color: solidblack;")
        self.completer_pendientes.popup().setStyleSheet("color: white; font-size: 13pt;"
                                                      "selection-background-color: #FF9B99;"
                                                      "selection-color: solidblack;")

    # Display

    def message(self, string, method, **kwargs):
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
            self.status_bar.showMessage(str(e), 10000)
        msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel | qtw.QMessageBox.Save)
        ret = msg.exec_()
        # msg.buttonClicked(qtw.QMessageBox.Ok).connect(lambda: print('method'))
        # msg.buttonClicked(qtw.QMessageBox.Cancel).connect(msg.close())
        if ret == qtw.QMessageBox.Ok:
            try:
                method.__call__()
            except Exception as e:
                self.status_bar.showMessage(str(e))
        elif ret == qtw.QMessageBox.Save:
            # método para exportar PDF / imprimir presupuesto sin guardarlo
            self.generar_pdf()

        else:
            msg.close()

    # Form methods
    @qtc.pyqtSlot()
    def complete_products(self, string, idx):
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
    def borrar_precios(self, idx):
        if len(self.sender().text()) == 0:
            try:
                print(idx)
                row, column, cols, rows = self.grid2.getItemPosition(idx)
                self.grid2.itemAtPosition(row, 5).widget().clear()
                self.grid2.itemAtPosition(row, 6).widget().clear()
                self.grid2.itemAtPosition(row, 7).widget().clear()
                self.display_total()
                #self.display_p_unitario()
            except Exception as e:
                print(e)

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
                self.status_bar.showMessage(str(e), 10000)
        else:
            self.trabajos_todos.clear()
            self.trabajos_todos.addItem('')
            self.trabajos_todos.addItems(sorted(self.presupuesto.loc[:, 'Motivo']))
            self.borrar_formulario()

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

                        print(self.completer_trabajos.completionModel().index(index, 0).data())
                        print(self.completer_trabajos.currentIndex().row())

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
            self.med_orig_cm_ancho.setText(str(subset['cto1'].values[0]))
            self.med_orig_cm_alto.setText(str(subset['cto2'].values[0]))
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
        # precios = [col for col in subset.columns if col.startswith('ctpreciouni')]
        # num_of_products = len(productos)
        item_row = 8
        for col in productos:
            producto_id = int(subset.loc[:, col].values[0])
            if producto_id != 0:
                item = self.productos[
                    self.productos['Contador'] == producto_id]['DenominaciónCompleta'].values[0]
                # print(item)
                self.grid2.itemAtPosition(item_row, 1).widget().setCurrentText(item)
                item_row += 1

    def completar_precios(self, subset):
        """Esta función completa con los precios con los que se fijaron presupuestos pasados"""
        precios = [col for col in subset.columns if col.startswith('ctpreciouni')]
        #print(precios)
        item_row = 8
        for col in precios:
            precio = subset.loc[:, col].values[0]
            if precio != 0:
                try:
                    self.grid2.itemAtPosition(item_row, 6).widget().setText(str(precio))
                    #print(precio, 'Done')
                    item_row += 1
                except Exception as e:
                    print(e)
                # print('Done', item_row, precio)
        #print('...')

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
                    print(item.objectName())
                elif item.objectName().startswith('p_') and len(item.text()) == 0:
                    item.setText('0')
                    print(item.objectName())
                elif item.objectName() == 'pp' and len(item.text()) == 0:
                    item.setText('0')
                    print(item.objectName())
                elif item.objectName() == 'var' and len(item.text()) == 0:
                    item.setText('0')
                    print(item.objectName())
                else:  # lineEdits de "otros"
                    if len(item.text()) == 0 and len(item.objectName()) != 0:
                        item.setText('S/D')
                        print(item.objectName())
        # print('Running other function')
        self.cargar_venta()

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
                print(col, e)
                pedido[col] = 0
        for col in text_cols:
            try:
                if len(pedido[col]) == 0:
                    pedido[col] = 'S/D'
            except Exception as e:
                print(col, e)
        return pedido

    def generar_pdf(self):
        """Generar un detalle de trabajo en PDF sin cargar los datos al CSV de presupuestos"""
        pedido = self.preparar_dic_datos()
        # print(pedido)
        count = 1
        col1 = 1  # columna de nombre
        col2 = 7  # columna de precios
        item_list = []
        for row in range(8, 16):
            producto = self.grid2.itemAtPosition(row, col1).widget().currentText()

            # print(producto)
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
        generate(pedido, path)
        self.status_bar.showMessage('PDF de orden generado correctamente.', 10000)

    def cargar_venta(self):
        """Cargar toda la información al CSV de presupuestos y generar orden de trabajo en PDF"""
        try:
            pedido = self.preparar_dic_datos()
            # print(pedido)
            count = 1
            col1 = 1  # columna de nombre
            col2 = 7   # columna de precios
            item_list = []
            for row in range(8, 16):
                producto = self.grid2.itemAtPosition(row, col1).widget().currentText()

                # print(producto)
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
                # print(count)

            dict_for_df = {key: value for key, value in pedido.items() if 'p_unitario' not in key}
            new_df = pd.DataFrame([dict_for_df])
            self.presupuesto = pd.concat([self.presupuesto, new_df], ignore_index=True)
            # print('Done')
            self.presupuesto.to_csv('database/DB/presupuestos_limpio.csv', index=False)

            # print('Saved')
            self.completers_from_presupuesto()
            self.status_bar.showMessage('Presupuesto cargado correctamente', 10000)
            # adding to combo boxes
            self.trabajos_todos.addItem(pedido['Motivo'])
            self.clientes_combo.addItem(pedido['Cliente'])
            self.presupuestos_pendientes.addItem(pedido['Motivo'])
            pedido['Lista_Items'] = item_list
            pedido['sup'] = self.sup_m2.text() or ''
            pedido['per'] = self.per_ml.text() or ''
            pedido['med_alto_final'] = self.med_final_cm_alto.text() or ''
            pedido['med_ancho_final'] = self.med_final_cm_ancho.text() or ''
            # generar pdf
            # print(pedido.keys())
            # generate(pedido)
            path = self.getPath()
            orden_trabajo(pedido, path)
        except Exception as e:
            self.status_bar.showMessage(str(e))

    @qtc.pyqtSlot()
    def completar_trabajo(self):
        # print('function')
        combobox_index = self.presupuestos_pendientes.currentIndex()
        cliente = self.cliente.text()
        motivo = self.motivo.toPlainText()
        # print(cliente, motivo)
        if len(cliente) > 0 and len(motivo) > 0:
            fecha = qtc.QDateTime.currentDateTime().toString('dd/MM/yyyy')
            index = self.presupuesto[
                (self.presupuesto['Cliente'] == cliente) & (self.presupuesto['Motivo'] == motivo)].index[0]
            #print(index)
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

        #print('Done')

    @qtc.pyqtSlot()
    def borrar_formulario(self):
        try:
            for i in range(self.grid1.count()):
                item = self.grid1.itemAt(i).widget()
                if isinstance(item, qtw.QComboBox):
                    item.clearEditText()
            for i in range(self.grid2.count()):
                item = self.grid2.itemAt(i).widget()
                if isinstance(item, qtw.QComboBox):
                    item.clearEditText()
                elif isinstance(item, qtw.QLineEdit) or isinstance(item, qtw.QTextEdit):
                    item.clear()
            self.med_final_cm_ancho.setText('0')
            self.med_final_cm_alto.setText('0')
            self.cantidad.setText('1')
            self.display_total()
            if isinstance(self.sender(), qtw.QPushButton):
                # restore original list
                self.trabajos_todos.clear()
                self.trabajos_todos.addItem('')
                self.trabajos_todos.addItems(sorted(self.presupuesto.loc[:, 'Motivo']))
        except Exception as e:
            print('e')
        #self.display_p_unitario()

    def borrar_presupuesto_cargado(self):
        cliente = self.cliente.text()
        motivo = self.motivo.toPlainText()
        # print(cliente, motivo)
        if len(cliente) > 0 and len(motivo) > 0:
            index = self.presupuesto[
                (self.presupuesto['Cliente'] == cliente) & (self.presupuesto['Motivo'] == motivo)].index[0]
            print(index)
            msg = qtw.QMessageBox()
            msg.setText(
                f'Está seguro de que desea borrar el trabajo de {cliente} con motivo: {motivo}?')
            msg.setStandardButtons(qtw.QMessageBox.Ok | qtw.QMessageBox.Cancel)
            ret = msg.exec_()
            if ret == qtw.QMessageBox.Ok:
                self.presupuesto.drop(index, axis='index', inplace=True)
                self.presupuesto.to_csv('database/DB/presupuestos_limpio.csv', index=False)
                self.status_bar.showMessage(
                    f'Se eliminó el trabajo de {cliente} con motivo "{motivo}".', 15000)
                self.borrar_formulario()
                self.completers_from_presupuesto()
            else:
                msg.close()
    # Cálculos

    @qtc.pyqtSlot()
    def calculo_medidas(self):
        # medidas originales
        ancho = self.med_orig_cm_ancho.text().replace(',', '.')
        alto = self.med_orig_cm_alto.text().replace(',', '.')
        pp = self.pp_cm.text().replace(',', '.')
        var = self.var.text().replace(',', '.')
        lst = [ancho, alto, pp, var]
        for txt in lst:
            if len(txt) == 0:
                lst[lst.index(txt)] = 0
            else:
                try:
                    lst[lst.index(txt)] = float(txt)
                except Exception as e:
                    lst[lst.index(txt)] = 0

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

    def calculo_total(self, ancho, alto):
        """Calcula el total unitario para cada item"""
        # print(ancho, alto)
        col = 6
        p_total = 0
        # si ya hay items elegidos:
        for row in range(8, 16):
            widget = self.grid2.itemAtPosition(row, col).widget()
            if len(widget.text()) > 0:
                # agarrar identificador de item y hacer cálculo según tipo en (row, 0)
                # varilla - m; vidrio, espejo, chapadur y  pp - sup.; pintura y patina - m y sup.
                item_id = self.grid2.itemAtPosition(row, 1).widget().lineEdit().text()[-1]
                # print('ID: ' + item_id)
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
    def display_total(self):
        """Muestra el total en la QLabel correspondiente"""
        total_final = 0
        if len(self.cantidad.text()) == 0:
            cantidad = 0
        elif len(self.cantidad.text()) != 0:
            cantidad = int(self.cantidad.text())
            for row in range(8, 20):
                if row != 16:
                    item = self.grid2.itemAtPosition(row, 7).widget()
                    if isinstance(item, qtw.QLineEdit):
                        text = self.grid2.itemAtPosition(row, 7).widget().text()
                        if len(text) > 0:
                            total_final += float(text)
        total_final = total_final * cantidad
        total_final = '%.2f' % total_final
        self.total.setText(str(total_final))

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

    def abrir_tabla_presupuestos(self):
        self.tabla = Tabla('database/DB/presupuestos_limpio.csv')
        self.tabla.exec_()

    def abrir_tabla_productos(self):
        self.tabla = Tabla('database/DB/productos.csv')
        self.tabla.exec_()



stylesheet = '''
#titulo {
color: #FF9B99;
font: bold;
font-size: 25pt;
font-family: Trebuchet MS;
}
QWidget {background-color: #2F5260;}

QLabel {
font-size: 15pt;
color: #F3E5CE;
}
#preciounitario {
border: 3px solid gray;
background-color: #5C7070;
border-style:outset;
border-width:3px;
border-color:ivory;
font-size: 17pt;

}
#preciototal {
border: 3px solid gray;
background-color: #5C7070;
border-style:outset;
border-width:3px;
border-color:ivory;
font-size: 17pt;
}
QTextEdit {
font-size: 13pt;
border: 1px solid black;
background-color: ivory;   
selection-background-color: #FF9B99;
selection-color: solidblack; 
}
QLineEdit {
    font-size: 13pt;
    border: 1px solid black;
    background-color: ivory;   
    selection-background-color: #FF9B99;
    selection-color: solidblack; 
}
QLineEdit:!enabled {
background-color: #BCC8C8;
color: #1D1E2C;
}
QComboBox {
subcontrol-origin: padding;
font-size: 13pt;
background-color: ivory;
color: black;
selection-background-color: #FF9B99;
selection-color: solidblack;
border-style: solid;
border-radius: 5px;
}
QComboBox:hover {
border: 1px #FF9B99;
}
QComboBox QAbstractItemView {
color: white;
}
QPushButton {
font-size: 13pt;
padding: 3px;
color: #F3E5CE;
}
QPushButton:hover {background: #A23E48;}
#menu {spacing: 3px; font-size: 10pt; color: #F3E5CE;}
#menu::item {padding: 1px 4px; background: transparent; border-radius: 6px;}
#menu::item:selected {background: #FF9B99;}

'''

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    app.setStyleSheet(stylesheet)
    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.
    mw = MainWindow()
    end = time.perf_counter()
    total = end - start
    print(f'Total: {total}')
    sys.exit(app.exec())
