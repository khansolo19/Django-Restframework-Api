from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .permissions import IsProfileAuthor
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ProfileSerializer, \
    ProfileUpdateSerializer, LogoutSerializer, ChangePasswordSerializer

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Successfully registration!', status=status.HTTP_201_CREATED)


class ActivationView(APIView):
    def get(self, request, activation_code):
        user = get_object_or_404(User, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Your account successfully activated!', status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response('Successfully log outed!', status=status.HTTP_204_NO_CONTENT)


# class BlacklistRefreshView(APIView):
#     def post(self, request):
#         token = RefreshToken(request.data.get('refresh'))
#         token.blacklist()
#         return Response("Success")

class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser, ]


class ProfileRetrieveAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )


class ProfileUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = (IsProfileAuthor,)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        object = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not object.check_password(request.data.get("old_password")):
                return Response({"old_password": ['Wrong password']}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            object.set_password(request.data.get("new_password"))
            object.is_active = True
            object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)