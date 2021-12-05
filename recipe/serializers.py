from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Recipe, Restaurant, RecipeVote
from base.serializers import AccountSerializer


class RestaurantSerializer(ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ('id', 'name')


class MenuSerializer(ModelSerializer):
    owner = RestaurantSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'owner')


class VoteSerializer(ModelSerializer):
    recipe = MenuSerializer(read_only=True)
    employee = AccountSerializer(read_only=True)
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeVote
        fields = ('id', 'recipe', 'employee', 'recipe_id')

