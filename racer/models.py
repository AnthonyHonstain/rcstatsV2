from django.db import models

from django.contrib.auth.models import User

from core.models import RacerId

class Follow(models.Model):
    user = models.ForeignKey(User)
    racerId = models.ForeignKey(RacerId)
    active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class Claim(models.Model):
    user = models.ForeignKey(User)
    racerId = models.ForeignKey(RacerId)
    active = models.BooleanField(default=False)
    # TODO - I haven't decided how or if to manage multiple 
    # conlficting names for the same racer
    #over_ride = models.ForeignKey(RacerId)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
     