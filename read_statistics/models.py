from django.db import models
from django.db.models.fields import exceptions
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# Create your models here.


class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)

    # 模型 先指向ContentType类型 blog模型对应ContentType对象
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 外键指向ContentType类型
    # 模型主键值
    object_id = models.PositiveIntegerField()   # 记录对应模型的主键值
    content_object = GenericForeignKey('content_type', 'object_id') # 把上两行统一起来变成通用的外键


class ReadNumExpandMethod:
    # 获取每一个博客文章的阅读数
    def get_read_num(self):
        try:
            # 获取ContentType对象对应的Blog模型
            ct = ContentType.objects.get_for_model(self)
            # 通过ContentType和其主键值获取ReadNum模型
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
            return readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0


class ReadDetail(models.Model):
    # 日期
    date = models.DateField(default=timezone.now)
    read_num = models.IntegerField(default=0)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

