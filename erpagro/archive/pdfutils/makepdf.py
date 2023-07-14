"""
The overall design of Platypus can be thought of has having several layers, top down, these are
- DocTemplates the outermost container for the document;
- PageTemplates specifications for layouts of pages of various kinds;
- Frames specifications of regions in pages that can contain flowing text or graphics.
- Flowables text or graphic elements that should be "flowed into the document (i.e. things like images, para-
  graphs and tables, but not things like page footers or fixed page graphics).
- pdfgen.Canvas the lowest level which ultimately receives the painting of the document from the other
  layers

canvas.setAuthor()
canvas.setTitle(title)
canvas.setSubject(subj)

p.line(x1,y1,x2,y2)
p.lines(linelist)
canvas.rect(x, y, width, height, stroke=1, fill=0)
canvas.grid(xlist, ylist)

canvas.setFillColor(magenta)
canvas.setFont(psfontname, size, leading = None)
canvas.stringWidth(self, text, fontName, fontSize, encoding=None)
canvas.drawString(x, y, text):
canvas.drawRightString(x, y, text)
canvas.drawCentredString(x, y, text)


canvas.drawImage(self, image, x, y, width=None, height=None, mask=None)

canvas.setLineWidth(width)
canvas.setLineCap(mode)
canvas.setLineJoin(mode)
canvas.setMiterLimit(limit)
canvas.setDash(self, array=[], phase=0)

canvas.saveState()
canvas.restoreState()

canvas.getPageNumber()
canvas.showPage()
"""

import inspect
import io
import locale
import textwrap

from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle

from django.contrib.staticfiles import finders
from reportlab.lib import utils

import purchases 
from accounts.models import Company


locale.setlocale(locale.LC_ALL, "")

def draw_logo(canvas, width, y=840):
    canvas.saveState()
    company = Company.objects.first()
    img_path = finders.find('images/logo.jpg')
    img = utils.ImageReader(img_path)
    iw, ih = img.getSize()
    height = ih*width/iw
    x = 30
    y = y - height
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(30+width/2, y-10, f"C.I.F {company.cif}")
    canvas.drawImage(img_path, 30, y, width=width, height=height, mask=None)
    canvas.restoreState()

def draw_company_data(canvas, y=765):
    company = Company.objects.first()
    canvas.saveState()
    data = []
    if company.post_box:
        data += [["APDO. CORREOS 24"]]
    if company.address_line:
        data +=  [[company.address_line]]
    if company.address_line2 and company.city:
        data += [[f"{company.address_line2} - {company.city}"]]           
    elif company.city:
        data += [[company.city]]
    if company.postal_code and company.state and company.country:
        data += [[f"{company.postal_code} {company.state} ({company.get_country_display()})"]]
    if company.phone:
        data += [[f"TEL. {company.phone}"]]
    if company.fax:
        data += [[f"FAX {company.fax}"]]
    if company.email:
        data += [["E-mail: admon@roquevicar.com"]]
    rowheights = [8] * len(data)
    colwidths = None
    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 6),])
    t.setStyle(tablestyle)
    table_width, table_height = t.wrap(0, 0)
    t.wrapOn(canvas, table_width, table_height)
    t.drawOn(canvas, 450, y)
    canvas.restoreState()

def draw_header_data(canvas, item, y=665, rowheights = None, fontsize=9):
    canvas.saveState()
    # draw invoice basic data
    data = [[f"{item._meta.verbose_name.upper()}:", f"{item.serial_number()}", "CÓDIGO:", f"{item.supplier.pk:05}"], 
            ["FECHA:", item.creation_date.date(), "N.I.F.:", f"{item.supplier.cif}"], 
            ]
    
    rowheights = rowheights
    colwidths = [None, 100, None, None]
    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", fontsize),])
    t.setStyle(tablestyle)
    table_width, table_height = t.wrap(0, 0)
    t.wrapOn(canvas, table_width, table_height)
    t.drawOn(canvas, 35, y)
    canvas.restoreState()
 
def draw_agent_address(canvas, agent, y=665, rowheights=None, fontsize=9):
    canvas.saveState()
    data = [[agent.name],
            [agent.address_line],
            [agent.city],
            [f"{agent.postal_code} {agent.state} ({agent.get_country_display()})"],
            ]
    rowheights = rowheights
    colwidths = None
    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", fontsize),])
    t.setStyle(tablestyle)
    table_width, table_height = t.wrap(0, 0)
    t.wrapOn(canvas, table_width, table_height)
    t.drawOn(canvas, 350, y)
    canvas.restoreState()

def draw_bottom_line(canvas, y=100, fontsize=6):
    canvas.saveState()
    company = Company.objects.first()
    canvas.setFont("Helvetica", fontsize)
    canvas.drawRightString(550, y, company.invoice_line)
    canvas.restoreState()

def draw_title(canvas, title, y=790):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(330, y , title)
    canvas.restoreState()


def make(item):
    if isinstance(item, purchases.models.Invoice):
        return purchases_invoice(item)
    if isinstance(item, purchases.models.Settlement):
        return purchases_settlement(item)
    if isinstance(item, purchases.models.EntryNote):
        return purchases_entrynote(item)

    raise TypeError(f"makepdf error: cannot make pdf from type {inspect.getmodule(item.__class__).__name__}.{item.__class__.__name__}")

def purchases_invoice(invoice):
    buffer = io.BytesIO() # file-like buffer
    p = canvas.Canvas(buffer, pagesize=A4) # Create the PDF object, using the buffer as its "file."

    # metadata
    p.setAuthor("mrio - mrio.dev@gmail.com")
    p.setTitle(f"{invoice.__class__.__name__} {invoice.serial_number()}")
    p.setSubject(f"Autofactura creada por ERPagro Software")

    # first page
    draw_bottom_line(p)
    draw_logo(p, 200)
    draw_header_data(p, invoice, rowheights=[None, 25])
    draw_agent_address(p, invoice.supplier)
    draw_company_data(p)

    # draw entrynotes+entries table 
    data = []
    rowheights = [None] 
    colwidths = [100, 340, 80]
    tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 10),
                             ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                             ])

    header = ["Nº Albarán", "Fecha", "Importe"]
    tablestyle.add("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    tablestyle.add("LINEBELOW", (0, 0), (-1, 0), 0.25, colors.black)
    data.append(header)
    rownum = 0
    for en in invoice.entrynote_set.all():
        rownum += 1
        rowheights.append(None)
        data.append([f"{en.pk:09}", 
                     en.creation_date.date(), 
                     f"{en.tax_amount():n}",
                     ])

    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    table_width, table_height = t.wrap(0, 0)
    t.setStyle(tablestyle)
    t.wrapOn(p, table_width, table_height)
    t.drawOn(p, 35, 655-table_height)

    # iva, retention, total
    p.line(35, 240, 565, 240)
    data = []
    rowheights = [12, 12, 30, 40]
    colwidths = [90, 80, 60]

    data.append(["Base Imponible", None, f"{invoice.tax_amount():n}"])
    data.append(["I.V.A.", f"{invoice.vat:n}%", f"{invoice.vat_amount():n}"])
    data.append([f"({invoice.get_type_display()})\nRetención", f"{invoice.irpf:n}%", f"{invoice.irpf_amount():n}"])
    data.append(["Total:", None, f"{invoice.total_amount():n}"])
    tablestyle = TableStyle([
                             ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                             ("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 14),
                             ("FONT", (0, 0), (-1, 1), "Helvetica-Bold"),
                             ])
    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    table_width, table_height = t.wrap(0, 0)
    t.setStyle(tablestyle)
    t.wrapOn(p, table_width, table_height)
    t.drawOn(p, 330, 230-table_height)
    p.showPage() # Close the PDF object cleanly, and we're done.


    draw_bottom_line(p)
    draw_logo(p, 200)
    draw_header_data(p, invoice, rowheights=[None, 25])
    draw_agent_address(p, invoice.supplier)
    draw_company_data(p)

    # draw entrynotes+entries table 
    data = []
    rowheights = [None] 
    colwidths =  [46, 46, 110, 30, 30, 30, 46, 46, 46, 46, 46,] #[45, 45, 110, 30, 30, 30, 48, 48, 48, 48, 48,]
    tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 7),
                             ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
                             ])
    header = ["Nº Albarán", "Fecha", "Género", "Bultos", "Kilos", "Precio", "Importe", "B.Impo", "Gasto", "Porte", "T.albar"]
    tablestyle.add("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    tablestyle.add("LINEBELOW", (0, 0), (-1, 0), 0.25, colors.black)
    data.append(header)
    rownum = 0
    for en in invoice.entrynote_set.all():
        rownum += 1
        rowheights.append(None)
        data.append([f"{en.pk:09}", 
                     en.creation_date.date(), 
                     None, None, None, None, None, 
                     f"{en.base_amount():n}",
                     f"{en.expenses():n}",
                     f"{en.carrier_expense():n}",
                     f"{en.tax_amount():n}"])
        tablestyle.add("FONT", (0, rownum), (-1, rownum), "Helvetica-Bold")
        for e in en.entry_set.all():
            rownum += 1
            agrofood_string = textwrap.wrap(f"{e.agrofood}", width=25)
            rowheights.append(len(agrofood_string)*8)
            data.append([None, None, 
                         "\n".join(agrofood_string), 
                         f"{e.packaging_transaction.number:n}", 
                         f"{e.weight:n}", 
                         f"{e.price:n}", 
                         f"{e.base_amount():n}", 
                         None, None, None, None])

    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    table_width, table_height = t.wrap(0, 0)
    t.setStyle(tablestyle)
    t.wrapOn(p, table_width, table_height)
    t.drawOn(p, 35, 655-table_height)
    # save and return
    p.showPage() # Close the PDF object cleanly, and we're done.
    p.save()
    buffer.seek(0)
    return buffer

def purchases_settlement(settlement):
    buffer = io.BytesIO() # file-like buffer
    p = canvas.Canvas(buffer, pagesize=A4) # Create the PDF object, using the buffer as its "file."

    # metadata
    p.setAuthor("mrio - mrio.dev@gmail.com")
    p.setTitle(f"{settlement.__class__.__name__}{settlement.serial_number()}")
    p.setSubject(f"Liquidación creada por ERPagro Software")

    # first page

    draw_bottom_line(p)
    draw_logo(p, 200)
    draw_header_data(p, settlement, rowheights=[None, 25])
    draw_agent_address(p, settlement.supplier)
    draw_company_data(p)

    # draw invoices table 
    baserowheight = 20
    data = []
    rowheights = []
    colwidths = [95] + [105]*4
    tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica"),
                             ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                             ])

    header = ["FACTURA", "BASE IMP.", "IVA", "RETENC.", "IMPORTE"]
    tablestyle.add("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    tablestyle.add("LINELEFT", (0, 0), (-1, -1), 0.25, colors.black) 
    tablestyle.add("BOX", (0, 0), (-1, -4), 0.25, colors.black) 
    tablestyle.add("BOX", (1, 0), (1, -4), 0.25, colors.black) 
    tablestyle.add("BOX", (3, 0), (3, -4), 0.25, colors.black) 
    tablestyle.add("LINERIGHT", (0, 0), (-1, 0), 0.25, colors.black)
    tablestyle.add("LINEBELOW", (0, 0), (-1, 0), 0.25, colors.black)
    tablestyle.add("LINEABOVE", (0, 0), (-1, 0), 0.25, colors.black)
    data.append(header)
    rowheights.append(baserowheight)
    for i in settlement.invoice_set.all():
        rowheights.append(baserowheight)
        data.append([f"{i.serial_number()}", 
                     f"{i.tax_amount():n}",
                     f"{i.vat_amount():n}",
                     f"{i.irpf_amount():n}",
                     f"{i.total_amount():n}",
                     ])

    rowheights.append(450 - len(data)*baserowheight)
    data.append([None] * 5)

    data.append(["TOTALES ...", 
                 f"{settlement.tax_amount():n}",
                 f"{settlement.vat_amount():n}",
                 f"{settlement.irpf_amount():n}",
                 None,
                 ])
    rowheights.append(baserowheight)

    data.append(["RECIBÍ CONFORME", None, None, None, "A PAGAR",])
    rowheights.append(baserowheight)
    data.append([None, None, None, None, f"{settlement.total_amount():n}",])
    rowheights.append(baserowheight)

    tablestyle.add("LINEABOVE", (0, -3), (-1, -3), 0.25, colors.black)
    tablestyle.add("FONT", (0, -2), (-1, -1), "Helvetica-Bold")
    tablestyle.add("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 12)

    # iva, irpf , total

    # draw table
    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    table_width, table_height = t.wrap(0, 0)
    t.setStyle(tablestyle)
    t.wrapOn(p, table_width, table_height)
    t.drawOn(p, 35, 645-table_height)

    # save and return
    p.showPage() # Close the PDF object cleanly, and we're done.
    p.save()
    buffer.seek(0)
    return buffer

def purchases_entrynote(entrynote):
    buffer = io.BytesIO() # file-like buffer
    p = canvas.Canvas(buffer, pagesize=A4) # Create the PDF object, using the buffer as its "file."

    # metadata
    p.setAuthor("mrio - mrio.dev@gmail.com")
    p.setTitle(f"{entrynote.__class__.__name__}-{entrynote.serial_number()}")
    p.setSubject(f"Albarán creado por ERPagro Software")

    # draw entries table 
    data = []
    rowheights = []
    colwidths = [70, 240, 70, 70, 70]
    tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica"),
                             ("FONT", (0, 0), (-1, -1), "Helvetica", 8),
                             ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                             ("VALIGN", (0, 0), (-1, 1), "MIDDLE"),
                             ("VALIGN", (0, 1), (-1, -1), "BOTTOM"),
                             ])

    header = ["PARTIDA", "PRODUCTO", "BULTOS", "K.NETOS", "PR.MÍNIMO"]
    tablestyle.add("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    tablestyle.add("FONT", (0, 1), (-1, -2), "Helvetica", 7)
    tablestyle.add("LINEBELOW", (0, 0), (-1, 0), 0.1, colors.black)
    tablestyle.add("LINEABOVE", (0, 0), (-1, 0), 0.1, colors.black)
    rowheights.append(18)
    data.append(header)
    first = True
    for e in entrynote.entry_set.all():
        if first:
            rowheights.append(16)
            first = False
        else:
            rowheights.append(12)
        data.append([f"{e.pk:08}", 
                     f"{e.agrofood}",
                     f"{e.packaging_transaction.number}",
                     f"{e.weight:n}",
                     None,
                     ])
    for _ in range(len(entrynote.entry_set.all()), 12):
        rowheights.append(12)
        data.append([None]*5)

    rowheights.append(18)
    data.append([None,
                 "TOTALES ...", 
                 f"{entrynote.packages():n}",
                 f"{entrynote.weight():n}",
                 None,
                 ])

    tablestyle.add("LINEABOVE", (0, -1), (-1, -1), 0.1, colors.black)
    tablestyle.add("FONT", (0, -1), (-1, -1), "Helvetica-Bold")


    # iva, irpf , total

    # draw table
    t = Table(data, colWidths=colwidths, rowHeights=rowheights)
    table_width, table_height = t.wrap(0, 0)
    t.setStyle(tablestyle)
    t.wrapOn(p, table_width, table_height)


    # DRAW
    p.setFont("Helvetica-Bold", 8)
    for y in [0, 421]:
        draw_logo(p, 180, y=y+419)
        draw_title(p, f"*ALBARÁN DE ENTRADA*", y=y+370)
        draw_company_data(p, y=y+344)
        draw_header_data(p, entrynote, y=y+289, rowheights=12, fontsize=8)
        draw_agent_address(p, entrynote.supplier, y=y+289, rowheights=12, fontsize=8)
        t.drawOn(p, 35, y+280-table_height)
        draw_bottom_line(p, y=y+85) 
        p.drawRightString(550, y + 70, "Fdo. El Productor.")

    # line division
    p.line(0, 421, 595, 421)
    
    for e in entrynote.entry_set.all():
        p.showPage()
        p.line(0, 421, 595, 421)
        # table
        data = [("TIPO DE CALIDAD", ":", f"{e.warehouse.quality}"),
                ("FECHA", ":", f"{e.entrynote.creation_date.date()}   ALBARÁN: {e.entrynote.pk:08}"),
                ("PRODUCTO", ":", f"{e.agrofood.pk:05}   {e.agrofood}"),
                ("CATEGORÍA", ":", f"{e.agrofood.get_quality_display().upper()}"),
                ("ORIGEN", ":", f"{e.warehouse.land.get_country_display().upper()} - {e.warehouse.land.state.upper()}"),
                (None,None,None),
                (None,None,None),
                ("PARTIDA", ":", f"{e.pk:08}"),
                ("BULTOS", ":", f"{e.packaging_transaction.number}"),
                ("KILOS", ":", f"{e.weight}"),
                (None,None,None),
                (None,None,None),
                ("CÓDIGO", ":", f"{e.entrynote.supplier.pk:05}"),
                ]
        srheight = 8
        brheight = 16 
        rowheights = [brheight, brheight, brheight, brheight, brheight, srheight, srheight, brheight, brheight, brheight,  srheight, srheight, brheight]
        colwidths = [120, 10, 300]
        tablestyle = TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 12),
                                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ])
        tablestyle.add("LINEBELOW", (0, 5), (-1, 5), 0.1, colors.black, None, (2,))
        tablestyle.add("LINEBELOW", (0, 10), (-1, 10), 0.1, colors.black, None, (2,))

        # draw table
        t = Table(data, colWidths=colwidths, rowHeights=rowheights)
        table_width, table_height = t.wrap(0, 0)
        t.setStyle(tablestyle)
        t.wrapOn(p, table_width, table_height)

        for y in [0, 421]:
            draw_logo(p, 180, y=y+419)
            draw_company_data(p, y=y+344)
            t.drawOn(p, 35, y+130)
            draw_bottom_line(p, y=y+85) 

    # save and return
    p.showPage() # Close the PDF object cleanly, and we're done.
    p.save()
    buffer.seek(0)
    return buffer

