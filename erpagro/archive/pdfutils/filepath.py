import os

from . import makepdf
from accounts.models import Company

def get_filename(instance):
    return f"{instance.serial_number()}.pdf"

def get_filepath(instance, filename=None):
    c = Company.objects.first()
    #get filename and filepath
    filename = get_filename(instance)
    filepath = os.path.join(f"{c.tax_start.year + 1}", f'{instance.__class__.__name__}')
    os.makedirs(filepath, exist_ok=True)
    pdf_save_path = os.path.join(filepath, filename)
    return pdf_save_path