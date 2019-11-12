from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import threading
from  django.template.loader import render_to_string


class SendMail(threading.Thread): #多线程处理
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text
        )

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)   #related_name解决外键对应冲突

    root = models.ForeignKey('self', related_name="root_comment", null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name="parent_comment", null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User,  related_name="replies", null=True, on_delete=models.CASCADE)
    #显示评论内容

    def send_mail(self):
        if self.parent is None:
            #评论我的博客
            subject = '有人评论你的博客'  # 主题
            email = self.content_object.get_email()
        else:
            #回复评论
            subject = '有人回复你的评论'
            email = self.reply_to.email
        if email != '':
            #text = '%s\n友情链接:<a href="%s">%s</a>' % (self.text, self.content_object.get_url(), '点击查看')  # 内容
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render_to_string('comment/send_mail.html', context)
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']
