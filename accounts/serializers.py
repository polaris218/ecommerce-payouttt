from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import User, FundingSource


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8)
    first_name = serializers.CharField(max_length=120, required=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPES, required=True)

    last_name = serializers.CharField(max_length=120, required=True)

    city = serializers.CharField(max_length=120, required=True)
    business_name = serializers.CharField(max_length=120, required=True)
    state = serializers.CharField(max_length=2, required=True)
    street_address = serializers.CharField(max_length=120, required=True)
    ssn = serializers.CharField(max_length=50, required=True)
    zip_code = serializers.IntegerField(required=True)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'], validated_data['password'],
                                        zip_code=validated_data.get('zip_code'))
        user.city = validated_data['city']
        user.state = validated_data['state']
        user.street_address = validated_data['street_address']
        user.full_name = validated_data.get('full_name')
        user.phone_number = validated_data.get('phone_number')
        user.first_name = validated_data.get('first_name')
        user.last_name = validated_data.get('last_name')
        user.business_name = validated_data.get('business_name')
        user.ssn = validated_data.get('ssn')
        if validated_data.get('user_type'):
            user.user_type = validated_data.get('user_type')

        return user

    class Meta:
        model = User
        fields = ('id', 'full_name', 'city', 'state', 'street_address', 'zip_code', 'email', 'password', 'phone_number',
                  'first_name', 'last_name', 'business_name', 'user_type', 'ssn')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['email', 'password', 'is_staff', 'is_active', 'date_joined']


class FundingSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingSource
        fields = ('source_url', 'user')


class BidFundingSourceSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = FundingSource
        fields = ('name', 'source_url', 'user')

    def get_user(self, obj):
        return obj.user.email


class IAVTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)


class PersonalAccount(serializers.Serializer):
    date_of_birth = serializers.DateField(required=True)
    ssn = serializers.CharField(max_length=12)


class UserProfileSerializer(serializers.ModelSerializer):
    funding_sources = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ['email', 'password', 'date_joined']

    def get_funding_sources(self, obj):
        return BidFundingSourceSerializer(obj.fundingsource_set.all(), many=True).data
