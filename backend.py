import io
import sys
import pdfrw
import json
from reportlab.pdfgen import canvas

def run():
    data = io.BytesIO()
    pdf = canvas.Canvas(data)
    template = pdfrw.PdfReader("PermisoDeAula1.pdf")
    request_data=open(sys.argv[1],"r")
    user_data = json.load(request_data)
    print(user_data)
    for page in template.Root.Pages.Kids:
        for field in page.Annots:
            label = field.T
            print(label)
            sides_positions = field.Rect
            left = min(sides_positions[0], sides_positions[2])
            bottom = min(sides_positions[1], sides_positions[3])
            value = user_data.get(label, '')
            print(value)
            padding = 2
            line_height = 0
            y=float(bottom)+padding+line_height
            x=float(left)+padding+10
            pdf.drawString(x=x, y=y, text=value)
        pdf.showPage()
    pdf.save()
    data.seek(0)
    return data

def merge(overlay_canvas: io.BytesIO, template_path: str) -> io.BytesIO:
    template_pdf = pdfrw.PdfReader(template_path)
    overlay_pdf = pdfrw.PdfReader(overlay_canvas)
    for page, data in zip(template_pdf.pages, overlay_pdf.pages):
        overlay = pdfrw.PageMerge().add(data)[0]
        pdfrw.PageMerge(page).add(overlay).render()
    form = io.BytesIO()
    pdfrw.PdfWriter().write(form, template_pdf)
    form.seek(0)
    return form

def save(form: io.BytesIO, filename: str):
    with open(filename, 'wb') as f:
        f.write(form.read())

if __name__ == '__main__':
    canvas_data = run()
    form = merge(canvas_data, template_path="./PermisoDeAula1.pdf")
    save(form, filename='out.pdf')
    sys.exit(0)
