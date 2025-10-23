from django.http import HttpResponse
from django.db import transaction

from my_test.models import Test, Contact, Tag

def testdb(request):
    test_delete = Test.objects.filter(name="monica").first()
    test_delete.delete()

    test_add = Test(name="monica", age=18) 
    test_modify = Test.objects.filter(name="monica").update(age=20)
    test_add.save()

    data_list = [
        Test(name='张三', age=25),
        Test(name='李四', age=30),
        Test(name='王五', age=28)
    ]
    created_list = Test.objects.bulk_create(data_list)
    print(f"created_list[0]: {created_list[0]}")
    
    test_list = list(Test.objects.all())
    # test_get = Test.objects.get(id=15)
    test_filter = Test.objects.filter(name="monica")
    test_order = Test.objects.order_by("name")[2:5]
    test_order1 = Test.objects.order_by("id")
    test_order2 = Test.objects.filter(name="monica").order_by("id")

    # print(f"test_list: {test_list}")
    # print("=== test_order (name排序后的第3~5条) ===")
    # for obj in test_order:
    #     print(obj)
    # print("\n=== test_order1 (按id排序) ===")
    # print(list(test_order1.values()))  # 转为字典列表

    # print("\n=== test_order2 (name=monica并按id排序) ===")
    # for obj in test_order2:
    #     print(f"ID:{obj.id} Name:{obj.name} Age:{obj.age}")  # 手动格式化

    response = ""
    for t in test_list:
        response += f"{t.id}: {t.name}: {t.age}<br>"

    contact_tag = [
        {
            'name': 'monica',
            'email': '1218526999@qq.com',
            'tags': ['泪失禁体质', '伟大的开发者']
        },
        {
            'name': '张三',
            'email': '2222222222@qq.com',
            'tags': ['普通用户']
        },
        {
            'name': '李四',
            'email': '3333333333@qq.com',
            'tags': ['VIP客户', '老客户']
        }
    ]
    
    try:
        with transaction.atomic():
            contact_list = []
            tag_list= []
            name_list = [data["name"] for data in contact_tag]
            for data in contact_tag:
                if Contact.objects.filter(name="monica").exists() == False:
                    contact_list.append(Contact(name=data["name"], email=data["email"]))
                else:
                    name_list.remove(data["name"])
            contact_list = Contact.objects.bulk_create(contact_list)
            print(f"----2----contact_list: {contact_list}")
            print(f"----2----name_list: {name_list}")

        with transaction.atomic():   
            contact_saved = Contact.objects.filter(name__in=name_list)
            name_id_map = {c.name: c.id for c in contact_saved}
            
            tag_list = []
            for data in contact_tag:
                name_ = data["name"]
                if name_ in name_id_map:
                    contact_id = name_id_map[name_]  # 通过name获取对应的contact_id
                    for tag_name in data["tags"]:
                        tag_list.append(Tag(contact_id=contact_id, tagname=tag_name))
            
            Tag.objects.bulk_create(tag_list)
    except Exception as e:
        print(f"操作失败：{e}")

    return HttpResponse("<p>" + response +"</p>")



