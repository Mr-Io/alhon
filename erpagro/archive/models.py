from django.db import models
from django.core.files import File

from .pdfutils import makepdf, get_filename, get_filepath 



# Create your models here.
class MakeFileAbstract(models.Model):
    pdf_file = models.FileField("archivo", max_length=256, upload_to=get_filepath, blank=True)

    def save(self, *args, **kwargs):                # WE STILL NEED A WAY TO CALL MAKE_PDF WHENEVER ONE OF THE CHILDS SAVE() 
        if self.pk:                                 # OR BE EXPLICIT ABOUT IT AND REMOVE SAVE() and DELETE() RELATIONSHIPTS
            self.make_pdf(save=False)               # OR USE SIGNALS...
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):              # IT IS BETTER TO USE SIGNALS SINCE BULK DELETIONS WONT TRIGGER THIS
        self.delete_pdf(save=False)
        return super().delete(*args, **kwargs)

    def delete_pdf(self, save=True):
        self.pdf_file.delete(save=save)

    def make_pdf(self, save=True):
        with makepdf.make(self) as f:
            file = File(f)
            self.pdf_file.delete(save=False)
            self.pdf_file.save(get_filename(self), file, save=save)
    
    class Meta:
        abstract = True