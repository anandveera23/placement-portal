from django.contrib import admin

# Register your models here.
from .models import Question

admin.site.register(Question)
from .models import CodingQuestion

admin.site.register(CodingQuestion)
