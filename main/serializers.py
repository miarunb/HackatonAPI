from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Category, Product, Review, Favorite

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'image')


class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def get_rating(self, instance):
        total_rating = sum(instance.reviews.values_list('rating', flat=True))
        reviews_count = instance.reviews.count()
        rating = total_rating / reviews_count if reviews_count > 0 else 0
        return round(rating, 1)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        return representation



class ReviewAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.first_name and not instance.last_name:
            representation['full_name'] = 'Анонимный пользователь'
            return representation


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ('id', 'author')

    def validate_product(self, product):
        request = self.context.get('request')
        if product.reviews.filter(author=request.user).exists():
            raise serializers.ValidationError('Вы не можете добавить второй отзыв на этот товар')
        return product

    def validate_rating(self, rating):
        if not rating in range(1, 6):
            raise serializers.ValidationError('Рейтинг должен быть от 1 до 5!')
        return rating

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['author'] = ReviewAuthorSerializer(instance.author).data
        return rep


class FavoriteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductDetailsSerializer(Product.objects.filter(favorites=instance.id),
                                                             many=True, context=self.context).data
        return representation