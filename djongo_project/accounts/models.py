from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin, Group)
from djongo import models


class Role(models.IntegerChoices):
    ADMIN = 0
    STAFF = 1
    NORMAL = 2


class CommonUserManager(BaseUserManager):
    def create_user(self,
                    username: str,
                    email: str,
                    birth: str,
                    password: str = None,
                    role: int = 2) -> 'CommonUser':
        user = self._default_set(username=username, email=email, birth=birth, password=password, role=role)
        user.save(using=self._db)
        return user

    def create_superuser(self,
                         username: str,
                         email: str,
                         birth: str,
                         password: str = None) -> 'CommonUser':
        user = self._default_set(username, email, birth, password=password)
        user.is_admin = True
        user.role = Role.ADMIN
        user.save(using=self._db)
        return user

    def create(self,
               username: str,
               email: str,
               birth: str,
               password: str = None) -> 'CommonUser':
        user = self._default_set(username, email, birth, password)
        user.save(using=self._db)
        return user

    def _default_set(self,
                     username: str,
                     email: str,
                     birth: str,
                     password: str = None,
                     role: int = 2) -> 'CommonUser':
        # <- 사용자 등록 시 암호화 실행 ->
        # Todo: 사용자 정보(이름, 나이, 성별, 주소 등)
        # return encrypted(name, age, sex, address)
        # <-->

        user = self.model(username=username, email=self.normalize_email(email), birth=birth, role=role)
        user.set_password(password)
        return user


class CommonUser(PermissionsMixin, AbstractBaseUser):
    # 사용자 정보의 필드는 암호화 타입(hex)으로 변경해야함: CharField -> TextField
    username = models.CharField(max_length=12, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    birth = models.DateField(null=True)
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.NORMAL)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CommonUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['birth', 'email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_activate(self):
        return self.is_active


class UserProfile(models.Model):
    user = models.OneToOneField(CommonUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13)
    address = models.CharField(max_length=150)
    description = models.TextField()


class GroupMap(models.Model):
    _id = models.ObjectIdField()
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE, related_name='user_group')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_user')
    date_joined = models.DateTimeField(auto_now_add=True, editable=True)
