from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Institution(models.Model):
	'''Some of the countries have fairly long names,
	assuming the schools may also have long names.'''
	country = models.CharField(max_length=100)
	name = models.CharField(max_length=200)


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="application_user")
    last_location = models.CharField(max_length=255)
    visited = models.TextField()
    institution = models.ForeignKey(Institution)

    def __unicode__(self):
        return self.user.username

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)

        if (len(self.visited) > 0):
            self.state_object = simplejson.loads(self.visited)
        else:
            self.state_object = {}

    def get_has_visited(self, section):
        has_visited = str(section.id) in self.state_object
        return has_visited

    def set_has_visited(self, sections):
        for s in sections:
            self.state_object[str(s.id)] = s.label

        self.visited = simplejson.dumps(self.state_object)
        self.save()

    def save_last_location(self, path, section):
        self.state_object[str(section.id)] = section.label
        self.last_location = path
        self.visited = simplejson.dumps(self.state_object)
        self.save()

    def display_name(self):
        return self.user.username



def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)



class LearningModule(models.Model):
	content = models.CharField(max_length=200)


