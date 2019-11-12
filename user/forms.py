from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='用户名或邮箱', widget=forms
                                .TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名或邮箱'}))#默认required为true，必须填写,不需要可以改为required=false
    password = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))#attrs为一个字典，可以加属性

    def clean(self):  #验证用户名密码
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user
        return self.cleaned_data  #方法必须返回cleaned_data

class RegForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=30, min_length=3, widget=forms
                                .TextInput(attrs={'class': 'form-control', 'placeholder': '请输入3-30位用户名'}))
    email = forms.CharField(label='邮箱', widget=forms
                               . EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}))
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'})
    )
    password = forms.CharField(label='密码', min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    password_again = forms.CharField(label='确认密码', min_length=6,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '再一次输入密码'}))

    def __init__(self, *args, **kwargs):  #实例化方法  为了传入request参数
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)   #初始化

    def clean(self):
        # 判断验证码
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已注册')
        return email

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

class ChangeNicknameForm(forms.Form):#修改昵称表
    nickname_new = forms.CharField(
        label='新的昵称',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'})
    )

    def __init__(self, *args, **kwargs):  #实例化方法   *args, **kwargs万能由，*args为任意类型参数，**kwargs为任意关键字的参数
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)   #初始化

    def clean(self):
        #判断对象是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()  #strip把前后空格去掉
        if nickname_new == '':
            raise forms.ValidationError("新的昵称不能为空")
        return nickname_new

class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'})
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'})
    )

    def __init__(self, *args, **kwargs):  #实例化方法   *args, **kwargs万能由，*args为任意类型参数，**kwargs为任意关键字的参数
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)   #初始化

    def clean(self):
        #判断对象是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        #判断用户是否已经绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定邮箱')

        #判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    # 验证邮箱是否已经被绑定
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被绑定')
        return email

    # 检查验证码是否为空
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

class ChangPasswordForm(forms.Form):
    old_password = forms.CharField(label='原密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入原密码'}))
    new_password = forms.CharField(label='新密码', min_length=6, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))
    new_password_again = forms.CharField(label='确认密码', min_length=6,
                                         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入新的密码'}))

    def __init__(self, *args, **kwargs):  #实例化方法  为了传入request参数
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangPasswordForm, self).__init__(*args, **kwargs)   #初始化

    def clean(self):
        #验证新的密码是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的新密码不一致')
        return self.cleaned_data

    def clean_old_password(self):
        #验证旧的密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧的密码错误')
        return old_password

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入绑定过的的邮箱'})
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'})
    )
    new_password = forms.CharField(label='新的密码', min_length=6,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')

        code = self.request.session.get('forgot_password_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return verification_code