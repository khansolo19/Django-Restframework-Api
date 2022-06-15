from rest_framework import serializers
from .models import Product, Category, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('slug', )


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'category', 'description', 'start_time', 'price', 'available', 'image')


    def _get_image_url(self, obj):
        if obj.image:
            url = obj.image.url
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(url)
            else:
                url = ''
            return url

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['image'] = self._get_image_url(instance)
        representation['likes'] = instance.likes.all().count()

        action = self.context.get('action')
        if action == 'retrieve':
            # detalizaciya
            representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        else:
            representation['comments'] = instance.comments.all().count()
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        validated_data['author_id'] = user_id
        post = Product.objects.create(**validated_data)
        return post

    def validate_title(self, title):
        if Product.objects.filter(slug=title.lower().replace(' ', '')).exists():
            raise serializers.ValidationError('Product with such name already exists')
        return title


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('user',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.email
        return representation
