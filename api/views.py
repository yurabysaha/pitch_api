from random import randint
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .models import Group
from .serializers import UserSerializer, GroupSerializer, AuthTokenSerializer, UserDetailSerializer
from .permissions import IsAdminOrReadOnly
from django.contrib.auth import get_user_model
from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class UserList(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    """Get or update current user or create new user.

    get: Get current user
    post: Create new user
    patch: Update current user
    delete: Remove current user
    """

    serializer_class = UserSerializer
    # permission_classes =

    def get_queryset(self):
        user = self.request.user.id
        return User.objects.filter(id=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['conf_code'] = randint(100000, 999999)
        user = User.objects.create_user(**serializer.validated_data)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response(data={'message': 'Code sent to phone number', 'token': token.key}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            users_data = serializer.validated_data.pop('friends', None)
            if users_data is not None:
                request.user.friends.add(*users_data)
            serializer.save()
            return Response(data={'message': 'Updated successful', 'user': serializer.data}, status=status.HTTP_200_OK)


class UserDetail(generics.RetrieveAPIView):
    """Actions with user by id.

    get: Get user profile by id
    """

    serializer_class = UserDetailSerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        user = self.kwargs['user_id']
        return User.objects.filter(id=user)


@api_view(['GET'])
def email_verify(request):
    """Verify if this email not exists."""
    if request.GET.get('email'):
        if User.objects.filter(email=request.GET.get('email')):
            return Response(data={'message': 'Email Already exist'}, status=status.HTTP_302_FOUND)
        else:
            return Response(data={'message': 'Email free'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def username_verify(request):
    """Verify if this username not exists."""
    if request.GET.get('username'):
        if User.objects.filter(email=request.GET.get('username')):
            return Response(data={'message': 'Username Already exist'}, status=status.HTTP_302_FOUND)
        else:
            return Response(data={'message': 'Username free'}, status=status.HTTP_200_OK)


class GroupList(generics.ListCreateAPIView):
    """Actions with groups.

    get: Get current user groups
    post: Create new group
    """

    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data={'message': 'group created', 'group': serializer.data}, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Group.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class GroupDetail(generics.RetrieveUpdateAPIView):
    """Actions with group by id.

    get: Get group by id
    patch: Update group by id
    """

    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated, )
    lookup_url_kwarg = 'group_id'

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return Group.objects.filter(id=group_id)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        users_data = request.data.pop('members', None)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if users_data is not None:
            instance.members.add(*users_data)
        serializer.save()
        return Response(data={'message': 'group updated', 'group': serializer.data}, status=status.HTTP_200_OK)


class ObtainAuthToken(APIView):
    """Get new token for user."""
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


obtain_auth_token = ObtainAuthToken.as_view()
