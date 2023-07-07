import random
from reportlab.platypus import Paragraph, BaseDocTemplate, Table, TableStyle, Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.colors import white, gray
from reportlab.lib.pagesizes import A4, LETTER, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import datetime


test1 = {'Cliente': 'Juan Román Riquelme',
         'Motivo': '''Cuadro de las 3 libertadores de America y la intercontinental
                   camiseta de Lionel''',
         'Cant': 6,
         'F_Entrega': '',
         'F_Recepción': '6/7/2023',
         'ctpp': 10,
         'ctvar': 10,
         'cto1': 10,
         'cto2': 10,
         'sup': 1,
         'per': 1,
         'med_ancho_final': 20,
         'med_alto_final': 20,
         'Lista_Items': ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                       'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                       'sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss',
                       'aaaaaaaaaaaaaaaaaaaaa'],
         'ctpreciouni1': 3456,
         'ctpreciouni2': 5423.5,
         'ctpreciouni3': 5555.55345,
         'ctpreciouni5': 2834,
         'p_unitario1': 1234,
         'p_unitario2': 4364,
         'p_unitario3': 2345,
         'p_unitario4': 4356}

pdfmetrics.registerFont(TTFont('Calibri', 'calibri-font-family/calibri-regular.ttf'))
pdfmetrics.registerFont(TTFont('Calibri Bold', 'calibri-font-family/calibri-bold.ttf'))

base_doc = BaseDocTemplate(
    filename='test.pdf',
    pagesize=A4,
    leftMargin=7,
    rightMargin=7,
    topMargin=15,
    bottomMargin=20

)
p_style = ParagraphStyle('motivo', fontSize=13, leading=20, wordWrap='CJK', font='Calibri',
                         spaceShrinkage=0.5)


def generate(dic, path=''):
    print('running generate')
    fecha = datetime.datetime.now().date()
    fecha = fecha.strftime('%d-%m-%Y')
    try:
        rn = random.randint(1, 300)
        name = f'{path}/{dic["Cliente"].replace(" ", "-")}-{fecha}--{rn}.pdf'
        # name = 'test.pdf'
        canvas = Canvas(name, pagesize=A4)
        width, length = A4
        print(width, length)

        canvas.setFont('Calibri Bold', 25)

        image = Image('png_aya.png', width=90, height=78)
        canvas.line(x1=10, y1=length - 20, x2=width - 10, y2=length - 20)
        canvas.drawString(40, length - 50, 'Presupuesto')
        canvas.setFont('Calibri Bold', 20)
        canvas.drawString(width / 2, length - 50, f'Fecha: {fecha}')

        print(dic["Cliente"], dic["Cliente"], str(dic["Cant"]))
        cliente = Paragraph(f'<b><u>Cliente</u></b>:  {dic["Cliente"]}', p_style)
        motivo = Paragraph(f'<b><u>Motivo</u></b>: {dic["Motivo"]}', p_style)
        cantidad = Paragraph(f'<b><u>Cantidad</u></b>: {str(int(dic["Cant"]))}', p_style)
        print('fase 2')
        #motivo.wrapOn(canvas, 400, 20)
        motivo.wrap(width-50, length)
        cliente.wrap(width-50, length)
        cantidad.wrap(width-50, length)

        cliente.drawOn(canvas, 40, length-100)
        motivo.drawOn(canvas, 40, length-165)
        cantidad.drawOn(canvas, 40, length-200)

        canvas.line(x1=10, y1=length-230, y2=length-230, x2=width-10)

        t_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 14), ('LEADING', (0, 0), (-1, -1), 25),
                              ('INNERGRID', (0, 0), (-1, -1), 0.5, 'black'),
                              ('BOX', (0, 0), (-1, -1), 2, 'black'),
                              ('ALIGN', (0, 0), (-1, -1), 'CENTER')])

        cell_style = ParagraphStyle('celdas', fontSize=13, leading=25, wordWrap='CJK')
        medidas = Table([[Paragraph('<b>Med. Original</b>', style=cell_style), '', '', ''],
                         ['Largo', str(dic["cto1"]), Paragraph('<b>Ancho varilla</b>', style=cell_style), str(dic["ctvar"])],
                         ['Ancho', str(dic["cto2"]), Paragraph('<b>Paspartú</b>', style=cell_style), str(dic["ctpp"])],
                         [Paragraph('<b>Med. Final cm</b>', style=cell_style), dic['med_alto_final'],
                          Paragraph('<b>Superficie m2</b>', style=cell_style), dic['sup']],
                         ['', dic["med_ancho_final"],  Paragraph('<b>Perímetro</b>', style=cell_style), dic['per']]])
        print('ongoing')
        medidas._argW[1], medidas._argW[3] = 70, 70  # cell width
        medidas._argW[0], medidas._argW[2] = 150, 150  # cell width
        medidas.setStyle(t_style)
        medidas.wrap(width, length)
        medidas.drawOn(canvas, width-510, length-400)

        canvas.line(x1=10, y1=length - 420, y2=length - 420, x2=width - 10)
        canvas.drawString(text='Productos: ', x=40, y=length-450)
        # productos = [dic[key] for key in dic.keys() if 'CCProducto' in key]
        # print(productos)
        productos = dic['Lista_Items']
        print(productos)
        count = 0
        for producto in productos:
            prod_string = Paragraph(f'<bullet>&bull</bullet>{producto}', style=p_style)
            prod_string.wrap(width, (length-700, length))
            # prod_list.append(prod_string)
            prod_string.drawOn(canvas, 40, length-(485+count))
            count += 25

        canvas.line(x1=10, y1=length - (500 + count), y2=length - (500 + count), x2=width - 10)

        p_unitario = '%.2f' % sum([float(dic[key]) for key in dic.keys() if 'ctpreciouni' in key])
        # print(p_unitario)
        p_total = '%.2f' % dic['Total_General']
        unitario = Paragraph(f'''<b><u>Precio unitario</u></b>: {p_unitario}''', p_style)
        total = Paragraph(f''' <b><u>Total</u></b>: {p_total}  ''', p_style)
        unitario.wrap(width, (length-820, length))
        total.wrap(width, (length-850, length))
        unitario.drawOn(canvas, 40, length - (530 + count))
        total.drawOn(canvas, 40, length - (560 + count))

        image.wrap(width, length)
        image.drawOn(canvas, width-160, length-740)

        cuit = Paragraph('CUIT: 20-37742928-2', p_style)
        cuit.wrap(width, length)
        cuit.drawOn(canvas, width-173, length-770)

        canvas.save()
    except Exception as e:
        print(str(e))


def orden_trabajo(dic, path=''):
    fecha = datetime.datetime.now().date()
    fecha = fecha.strftime('%d-%m-%Y')
    rn = random.randint(1, 300)
    name = f'{path}/OrdenTrabajo-{dic["Cliente"].replace(" ", "-")}-{fecha}--{rn}.pdf'
    paragraph_style = ParagraphStyle('style', fontSize=10, leading=11, wordWrap='CJK', font='Calibri',
                                     spaceShrinkage=0.5)
    canvas = Canvas(name, pagesize=A4)
    width, length = A4
    cliente = dic['Cliente']
    cantidad = dic['Cant']
    motivo = dic['Motivo']
    canvas.setFont('Calibri', 10)
    f_entrega = dic['F_Entrega'] if not 'S/D' else ''
    canvas.drawString(x=100, y=length-20, text=f'Fecha Entrega: {f_entrega}')
    canvas.drawString(x=350, y=length-20, text=f'Fecha Recepción: {dic["F_Recepción"]}')
    canvas.line(x1=60, y1=length-30, x2=width-60, y2=length-30)

    canvas.setFont('Calibri', 14)
    canvas.drawString(x=60, y=length-60, text=f'CLIENTE: {cliente.upper()}')
    canvas.drawString(x=373, y=length-60, text=f'Cant:      {cantidad}')
    par_motivo = Paragraph(f'Motivo:  {motivo}', paragraph_style)
    # canvas.drawString(x=60, y=length-90, text=f'Motivo:  {motivo}')
    par_motivo.wrap(245, length)
    par_motivo.drawOn(canvas, x=60, y=length-120)

    t_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 9), ('LEADING', (0, 0), (-1, -1), 4),
                          #('INNERGRID', (0, 0), (-1, -1), 0.5, 'black'),
                          #('BOX', (0, 0), (-1, -1), 2, 'black'),
                          ('ALIGN', (0, 0), (-1, -1), 'CENTER')])

    cell_style = ParagraphStyle('celdas', fontSize=9, leading=8, wordWrap='CJK')
    medidas = Table([['', '', '', ''],
                     [Paragraph('<b>Med. Original</b>', style=cell_style), str(dic["cto1"]), Paragraph('<b>Ancho varilla</b>', style=cell_style),
                      str(dic["ctvar"])],
                     ['', str(dic["cto2"]), Paragraph('<b>Paspartú</b>', style=cell_style), str(dic["ctpp"])],
                     [Paragraph('<b>Med. Final cm</b>', style=cell_style), dic['med_alto_final'],
                      Paragraph('<b>Superficie m2</b>', style=cell_style), dic['sup']],
                     ['', dic["med_ancho_final"], Paragraph('<b>Perímetro</b>', style=cell_style), dic['per']]])
    medidas._argW[1], medidas._argW[3] = 30, 30  # cell width
    medidas._argW[0], medidas._argW[2] = 100, 100  # cell width
    medidas.setStyle(t_style)
    medidas.wrap(width-50, length)
    medidas.drawOn(canvas, 310, length - 150)

    canvas.line(x1=60, y1=length - 170, x2=width - 60, y2=length - 170)

    # print(productos)
    canvas.setFont('Calibri Bold', 12)
    canvas.drawString(x=100, y=length-185, text='Nombre de Producto')
    canvas.drawString(x=360, y=length-185, text='P. Unitario')
    canvas.drawString(x=440, y=length-185, text='Importe')
    productos = dic['Lista_Items']
    lst_unitario = [dic[p] for p in dic.keys() if 'p_unitario' in p]
    lst_unitario = [p for p in lst_unitario if float(p) > 0]
    lst_relativo = [dic[p] for p in dic.keys() if 'ctpreciouni' in p]
    lst_relativo = [p for p in lst_relativo if float(p) > 0]
    count = 0
    paragraph_style = ParagraphStyle('style', fontSize=10, leading=10, wordWrap='CJK', font='Calibri',
                                     spaceShrinkage=0.5)
    print(len(productos), len(lst_unitario), len(lst_relativo))
    for producto in productos:
        prod_string = Paragraph(f'{producto}', style=paragraph_style)
        prod_string.wrap(305, length)
        # prod_list.append(prod_string)
        prod_string.drawOn(canvas, 50, length - (210 + count))

        index = productos.index(producto)
        p_unit = lst_unitario[index]
        unit_par = Paragraph(f'{p_unit}', style=paragraph_style)
        unit_par.wrap(430, length)
        unit_par.drawOn(canvas, 375, length - (210 + count))

        p_re = lst_relativo[index]
        p_re_par = Paragraph(f'<b>{p_re}</b>', style=paragraph_style)
        p_re_par.wrap(width, length)
        p_re_par.drawOn(canvas, 450, length - (210 + count))
        print(index)
        count += 20

    otros = [dic[o] for o in dic.keys() if 'ctotros' in o]
    otros = [o for o in otros if o not in 'S/D']
    otros_precios = [dic[o] for o in dic.keys() if 'cttotalotros' in o]
    otros_precios = [p for p in otros_precios if str(p) not in '0']
    for otro in otros:
        otro_par = Paragraph(f'{otro}', style=paragraph_style)
        otro_par.wrap(305, length)
        otro_par.drawOn(canvas, 50, length - (400 + count))

        index = otros.index(otro)
        precio = otros_precios[index]
        par = Paragraph(f'<b>{precio}</b>', style=paragraph_style)
        par.wrap(width, length)
        par.drawOn(canvas, 450, length - (400 + count))
        count += 20

    paragraph_style = ParagraphStyle('style', fontSize=14, leading=10, wordWrap='CJK', font='Calibri',
                                     spaceShrinkage=0.5)
    unitario = Paragraph('Unitario', style=paragraph_style)
    total = Paragraph('Total', style=paragraph_style)
    p_unitario_total = '%.2f' % sum([float(dic[key]) for key in dic.keys() if 'ctpreciouni' in key])
    p_total = '%.2f' % dic['Total_General']
    unitario.wrap(width, length)
    unitario.drawOn(canvas, 350, length - 600)

    total.wrap(width, length)
    total.drawOn(canvas, 350, length - 630)

    p_unitario_total_par = Paragraph(f'<b>{p_unitario_total}</b>', style=paragraph_style)
    p_total_par = Paragraph(f'<b>{p_total}</b>', style=paragraph_style)

    p_unitario_total_par.wrap(width, length)
    p_total_par.wrap(width, length)

    p_unitario_total_par.drawOn(canvas, 450, length - 600)
    p_total_par.drawOn(canvas, 450, length - 630)


    # image = Image('png_aya.png', width=90, height=78)

    canvas.save()
    #print(width, length)


if __name__ == '__main__':
    # generate(test1)
    orden_trabajo(dic=test1)
