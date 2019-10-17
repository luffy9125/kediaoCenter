import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# Create your models here.


# 多线程处理发送邮件,节约时间
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject,
                  '',
                  settings.EMAIL_HOST_USER,
                  [self.email],
                  fail_silently=self.fail_silently,
                  html_message=self.text
                  )


# 评论模型
class Comment(models.Model):
    # content_type 应用 模型(表)与模型(表)之间的桥梁
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 外键指向ContentType类型
    # 模型主键值
    object_id = models.PositiveIntegerField()   # 记录对应模型的主键值
    content_object = GenericForeignKey('content_type', 'object_id') # 把上两行统一起来变成通用的外键

    # 评论内容
    text = models.TextField()
    # 评论时间
    comment_time = models.DateTimeField(auto_now_add=True)
    # 评论人
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)

    # 获取一条评论下边所有的回复
    root = models.ForeignKey('self', related_name="root_comment", null=True, on_delete=models.CASCADE)
    # 一级评论
    parent = models.ForeignKey('self', related_name="parent_comment", null=True, on_delete=models.CASCADE)
    # 回复哪个?
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)

    # 邮件发送节省时间处理方法
    def send_mail(self):
        # 发送邮件通知
        if self.parent is None:
            # 评论我的博客
            subject = '有人评论你的博客'  # 主题
            # 发送邮件到这篇文章的作者
            email = self.content_object.get_email()
        else:
            # 回复评论
            subject = '有人回复你的评论'  # 主题
            # 发送邮件到回复你的用户
            email = self.reply_to.email
        if email != '':
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            # 邮件内容
            text = render_to_string('comment/send_mail.html', context)
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.text

    class META:
        ordering = ['comment_time']
