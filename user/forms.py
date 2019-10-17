from django import forms
from django.contrib import auth
from django.contrib.auth.models import User


# 登录
class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='用户名或邮箱', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名或邮箱'}))
    password = forms.CharField(
        label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))

    # 清理有问题的验证行为
    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']

        # 验证登录
        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            # 用username判断,如判断不到就用email
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                # 验证user是否为None,如不为None则验证通过,验证通过就可以往下执行代码去登录
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user

        return self.cleaned_data


# 注册
class RegForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        max_length=30,
        min_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入3-30位用户名'}))
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}))
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    password = forms.CharField(
        label='密码',
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    password_again = forms.CharField(
        label='再输入一次密码',
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再输入一次密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            # 剔除user并赋值给self.user
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    # 评论对象
    def clean(self):
        # 判断验证码
        code = self.request.session.get('register_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    # 用户名验证
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    # 邮箱验证
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    # 密码验证
    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again

    # 验证码输入框里的验证码是否为空
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == "":
            raise forms.ValidationError('验证码不能为空')
        return verification_code


# 修改昵称
class ChangeNicknameForm(forms.Form):
    nickname_new = forms.CharField(
        label='新的昵称', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'})
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            # 剔除user并赋值给self.user
            self.user = kwargs.pop('user')
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    # 评论对象
    def clean(self):
        # 数据检查
        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    # 修改昵称前判断昵称是否为空
    def clean_nickname_new(self):
        nickname_new = self.cleaned_data.get('nickname_new', '').strip()
        if nickname_new == '':
            raise forms.ValidationError("新的昵称不能为空")
        return nickname_new


# 绑定邮箱
class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(
            attrs={'class':'form-control', 'placeholder': '请输入正确的邮箱'}
        )
    )
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            # 剔除user并赋值给self.user
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    # 评论对象
    def clean(self):
        # 数据检查
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断用户是否已绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('你已经绑定了邮箱')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    #  验证邮箱是否已存在,如已存在则不能继续绑定
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱已经被绑定')
        return email

    # 验证码输入框里的验证码是否为空
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == "":
            raise forms.ValidationError('验证码不能为空')
        return verification_code


# 修改密码
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='旧密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入旧的密码'}))
    new_password = forms.CharField(
        label='新密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))
    new_password_again = forms.CharField(
        label='再次输入新密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入新的密码'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            # 剔除user并赋值给self.user
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    # 评论对象
    def clean(self):
        # 验证新的密码两次输入是否一致
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次输入的密码不一致')
        return self.cleaned_data

    # 验证旧密码是否正确
    def clean_old_password(self):
        # 验证旧的密码是否正确
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧密码错误')
        return old_password


# 忘记密码
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入绑定过的邮箱'}))
    verification_code = forms.CharField(
        label='验证码',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    new_password = forms.CharField(
        label='新密码', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新的密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            # 剔除user并赋值给self.user
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    # 验证username
    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email

    # 验证码输入框里的验证码是否为空
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == "":
            raise forms.ValidationError('验证码不能为空')

        # 判断验证码
        code = self.request.session.get('forgot_password_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码不正确')


        return verification_code