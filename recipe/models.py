from django.db import models
from django.db.models import Max, Count
from django.utils.datetime_safe import date
from datetime import timedelta

from base.models import Account as User


class RestaurantManager(models.Manager):
    def create_restaurant(self, name, current_user):
        user = User.objects.filter(username=current_user).first()
        return Restaurant.objects.create(name=name, owner=user)

    def get_restaurant_list(self):
        return Restaurant.objects.select_related('owner').order_by('-id')

    def get_current_user_restaurant(self, current_user):
        user = User.objects.filter(username=current_user).first()
        return Restaurant.objects.filter(owner=user).select_related('owner').first()  # only single restaurant per owner


class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RestaurantManager()


class RecipeManager(models.Manager):
    def create_menu(self, name, current_user):
        user = User.objects.filter(username=current_user).first()
        restaurant = Restaurant.objects.filter(owner=user).first()   # Due to lack of time, current design only supports
        return Recipe.objects.create(owner=restaurant, name=name)    # single restaurant for a particular owner!

    def get_all_available_menu(self):
        return Recipe.objects.filter(is_available=True).select_related('owner').order_by('id')


class Recipe(models.Model):    # my bad, wrong naming, it should be Menu !
    owner = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RecipeManager()


class RecipeVoteManager(models.Manager):

    def save_vote(self, employee, recipe_id):
        """
        Single employee can vote a menu for current date
        return false if already voted
        """
        user = User.objects.filter(username=employee).first()
        menu = Recipe.objects.filter(pk=recipe_id).first()
        if not RecipeVote.objects.filter(recipe=menu, employee=user, created_at__startswith=date.today()).exists():
            RecipeVote.objects.create(recipe=menu, employee=user)
            return True
        return False

    def get_vote_status(self):
        q = RecipeVote.objects.filter(created_at__startswith=date.today())
        return q.select_related('recipe').values('recipe__name', 'recipe__owner__name').annotate(vote_count=Count('pk'))


class RecipeVote(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    employee = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RecipeVoteManager()


class VoteResultTrackerManager(models.Manager):

    def get_vote_result(self):
        v_status = RecipeVote.objects.get_vote_status()
        top_restaurant = v_status.latest('vote_count')  # get top voted recipe and restaurant
        yesterday_res = VoteResultTracker.objects.filter(created_at__gte=date.today() - timedelta(1),
                                                         restaurant_name=top_restaurant['recipe__owner__name']).exists()
        two_day_ago_res = VoteResultTracker.objects.filter(created_at__gte=date.today() - timedelta(2),
                                                           restaurant_name=top_restaurant['recipe__owner__name']).exists()

        if yesterday_res and two_day_ago_res:
            second_highest_vote = list(v_status)[1]
            VoteResultTracker.objects.create(restaurant_name=second_highest_vote['recipe__owner__name'])
            return {'restaurant_name': second_highest_vote['recipe__owner__name'],
                    'recipe_name': second_highest_vote['recipe__name']}
        return {'restaurant_name': top_restaurant['recipe__owner__name'], 'recipe_name': top_restaurant['recipe__name']}


class VoteResultTracker(models.Model):
    restaurant_name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VoteResultTrackerManager()
