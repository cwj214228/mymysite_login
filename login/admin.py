from django.contrib import admin
from . import models

# 把models注册到admin里面
admin.site.register(models.User)
