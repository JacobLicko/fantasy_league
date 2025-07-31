from django.db import models
import string, random
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
def generate_unique_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class League(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=8, unique=True, default=generate_unique_code)
    members = models.ManyToManyField(User, related_name='leagues')
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        User,
        related_name = 'created_leagues',
        on_delete = models.CASCADE,
        null = True,
        blank = True,
    )
    max_players = models.PositiveSmallIntegerField(
        choices=[(2,'2'),(4,'4'),(6,'6'),(8,'8')],
        default=2
    )
    draft_type = models.CharField(
        max_length = 10,
        choices=[('snake','Snake'),('auction','Auction')],
        default='snake'
    )
    region = models.CharField(
        max_length = 10,
        choices=[('NACL','NACL')],
        default = 'NACL'
    )
    draft_date = models.DateField(null = True, blank = True)
    draft_time = models.TimeField(null = True, blank = True)

    def __str__(self):
        return f"{self.name} ({self.code})"
    
class DraftSession(models.Model):
    league = models.OneToOneField('League',on_delete=models.CASCADE,related_name='draft_session')
    start_time = models.DateTimeField()
    expires_at = models.DateTimeField()
    ready = models.ManyToManyField(User, blank=True)
    started = models.BooleanField(default=False)

    @classmethod
    def start_for_league(cls, league):
        # Create or reset the DraftSession for this Leauge.
        now = timezone.now()
        expires = now + timedelta(minutes=2)
        session, _ = cls.objects.update_or_create(league=league, defaults={'start_time' : now, 'expires_at': expires})

        # Clear out any old ready flags when restarting
        session.ready.clear()
        session.started = False
        session.save()
        return session
    
    def is_expired(self):
        # Once completed, we never expire it
        if self.started:
            return False
        return timezone.now() > self.expires_at