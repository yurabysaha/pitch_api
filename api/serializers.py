# api/serializers.py
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from .models import Group
from rest_framework import serializers, request

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username', 'phone', 'first_name', 'last_name', 'date_of_birth', 'allow_follow', 'friends', )
        extra_kwargs = {
            'friends': {'many': True, 'required': False},
            'phone': {'required': True}
        }


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_of_birth', 'allow_follow', 'friends', )


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name', 'members', 'owner', )
        extra_kwargs = {
            'owner': {'read_only': True},
            'members': {'many': True}
        }


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg, code='authorization')
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
