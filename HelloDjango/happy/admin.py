from django.contrib import admin

from . import models


@admin.register(models.AuthorDetail)
class AuthorDetailAdmin(admin.ModelAdmin):
    list_display = ('get_author', 'tel', 'addr')  # 自定义列表页
    
    def get_author(self, obj):
        return obj.author.name  # 通过关联字段获取作者名
    get_author.short_description = '作者'  # 设置列标题

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_publish', 'price')
    search_fields = ('title',)
    
    def display_publish(self, obj):
        return obj.publish.name
    display_publish.short_description = '出版社'

# 一次性注册剩余模型（使用默认配置）
admin.site.register([models.Author, models.Publish])