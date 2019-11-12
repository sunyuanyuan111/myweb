from django.contrib import admin
from .models import BlogType, Blog

class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')

class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'blog_type', 'author', 'get_read_num', 'created_time', 'last_updated_time')

#class ReadNumAdmin(admin.ModelAdmin):
 #   list_display = ('read_num', 'blog')

#注册模块
admin.site.register(BlogType, BlogTypeAdmin)
admin.site.register(Blog, BlogAdmin)
#admin.site.register(ReadNum, ReadNumAdmin)