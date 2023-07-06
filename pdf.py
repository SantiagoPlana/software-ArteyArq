import random
from reportlab.platypus import Paragraph, BaseDocTemplate, Table, TableStyle, Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.colors import white, gray
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import datetime


# test1 = {'Cliente': 'Juan Román Riquelme',
#         'Motivo': '''Cuadro de las 3 libertadores de America y la intercontinental
#                   camiseta de Lionel''',
#         'Cantidad': 6}
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
p_style = ParagraphStyle('motivo', fontSize=15, leading=20, wordWrap='CJK', font='Calibri',
                         spaceShrinkage=0.5)


def generate(dic, path=''):
    print('running generate')
    fecha = datetime.datetime.now().date()
    fecha = fecha.strftime('%d-%m-%Y')
    try:
        rn = random.randint(1, 300)
        name = f'{dic["Cliente"].replace(" ", "-")}-{fecha}--{rn}.pdf'
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

        t_style = TableStyle([('FONTSIZE', (0, 0), (-1, -1), 15), ('LEADING', (0, 0), (-1, -1), 25),
                              ('INNERGRID', (0, 0), (-1, -1), 0.5, 'black'),
                              ('BOX', (0, 0), (-1, -1), 2, 'black'),
                              ('ALIGN', (0, 0), (-1, -1), 'CENTER')])

        cell_style = ParagraphStyle('celdas', fontSize=15, leading=25, wordWrap='CJK')
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
            prod_string.drawOn(canvas, 40, length-(475+count))
            count += 25

        canvas.line(x1=10, y1=length - (500 + count), y2=length - (500 + count), x2=width - 10)

        p_unitario = round(sum([dic[key] for key in dic.keys() if 'ctpreciouni' in key]))
        # print(p_unitario)
        p_total = round(dic['Total_General'])
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



#if __name__ == '__main__':
    # generate(test1)

