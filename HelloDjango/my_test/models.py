from django.db import models as m

# Create your models here.

#类名代表了数据库表名 Test
class Test(m.Model):
    # name 字段代表数据表中的字段(name), 数据类型则是CharField
    name = m.CharField(max_length=20)
    age = m.IntegerField(default=0)

    class Meta:
        db_table = 'my_test_test'  # 显式指定表名

    def __str__(self):
        return f"ID:{self.id} {self.name} {self.age}"  # 添加友好的打印格式

class Contact(m.Model):
    name = m.CharField(max_length=20, unique=True)
    email = m.EmailField(unique=True)

    class Meta:
        verbose_name = "联系人"
    
    def __str__(self):
        return f"id:{self.id} name:{self.name} email:{self.email}"
class Tag(m.Model):
    contact = m.ForeignKey(
        Contact, 
        on_delete=m.CASCADE,
        related_name="tags",  # 反向查询名称
        verbose_name="所属联系人"
        )
    tagname = m.CharField(max_length=50, verbose_name="标签名称")
    
    def __str__(self):
        return f"contact_id:{self.contact_id} {self.tagname}"
