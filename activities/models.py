from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db.models.query_utils import Q
from django.db.models.signals import pre_save, post_init
from django.dispatch.dispatcher import receiver
from django.utils import simplejson
from operator import itemgetter
from pagetree.models import PageBlock
from quizblock.models import Quiz, Answer, Question, Submission

class DosageActivity(Quiz):
    class Meta:
        proxy = True

#need to override behavior of submit
    def submit(self, user, data):
        question = ''
        user_answer = ''
        answer = ''
        for k in data.keys():
            #identify question we are dealing with
            if k.startswith('question'):
                qid = int(k[len('question'):])
                question = Question.objects.get(id=qid)
            #grab the correct answer
                answer = Answer.objects.get(question=question)
            #find the users answer
            if k.startswith('value'):
                user_answer = k
                print k
                
#                 if isinstance(data[k], list):
#                     for v in data[k]:
#                         Response.objects.create(
#                             submission=s,
#                             question=question,
#                             value=v)
#                 else:
#                     Response.objects.create(
#                         submission=s,
#                         question=question,
#                         value=data[k])
#         s = Submission.objects.create(quiz=self, user=user)
        


#may have to override unlocked as well 
#     def unlocked(self, user):
#         # meaning that the user can proceed *past* this one,
#         # not that they can access this one. careful.
#         return Submission.objects.filter(quiz=self, user=user).count() > 0




# is this necessary?
#class DosageAnswer(models.Model):
#    correct = models.BooleanField()
#    correct_response = models.CharField(max_length=10)


# class ActivityState (models.Model):
#     user = models.ForeignKey(User, unique=True,
#                           related_name="dosage_activity_user")
#     json = models.TextField()
#  
#     @classmethod
#     def get_for_user(cls, user):
#         try:
#             stored_state = ActivityState.objects.get(user=user)
#         except ActivityState.DoesNotExist:
#             # setup the template
#             state = {}
#             stored_state = ActivityState.objects.create(
#                 user=user, json=simplejson.dumps(state))
#         return stored_state
#  
#     @classmethod
#     def clear_for_user(cls, user, patient_id):
#         state = ActivityState.objects.get(user=user)
#         #state.data['patients'][patient_id] = {}
#         #state.save()
# 
# 
# @receiver(post_init, sender=ActivityState)
# def post_init_activity_state(sender, instance, *args, **kwargs):
#     instance.data = simplejson.loads(instance.json)
#  
#   
# @receiver(pre_save, sender=ActivityState)
# def pre_save_activity_state(sender, instance, *args, **kwargs):
#     instance.json = simplejson.dumps(instance.data)
# 
# 
# class DosageActivityBlock(models.Model):
#     template_file = ""#activity_virtual_patient/patient.html"
#     css_template_file = ""#activity_virtual_patient/patient_css.html"
#     js_template_file = ""#activity_virtual_patient/patient_js.html"
#     display_name = ""#Virtual Patient"
# 
#     pageblocks = generic.GenericRelation(PageBlock)
#     user_answer = models.CharField(max_length=5)
#     correct_answer =  models.CharField(max_length=5)
#     correct = models.BooleanField()
# 
#     def pageblock(self):
#         return self.pageblocks.all()[0]
# 
#     def __unicode__(self):
#         return unicode(self.pageblock())
# #???
#     def needs_submit(self):
#         return self.view != 'RS'
# #    patient = models.ForeignKey(Patient)
# 
#     def submit(self, user, data):
#         state = ActivityState.get_for_user(user)
# 
#         if self.user_answer == self.correct_answer:
#             state.save()
# 
#         else:
#             return False
# 
#     def redirect_to_self_on_submit(self):
#          return False
#  
#     @classmethod
#     def add_form(self):
#         return PatientAssessmentForm()
#  
#     def edit_form(self):
#         return PatientAssessmentForm(instance=self)
#  
#     @classmethod
#     def create(self, request):
#         form = PatientAssessmentForm(request.POST)
#         return form.save()
#  
#     def edit(self, vals, files):
#         form = PatientAssessmentForm(data=vals, files=files, instance=self)
#         if form.is_valid():
#             form.save()
#  
#     def unlocked(self, user):
#         state = ActivityState.get_for_user(user)
# 
#         if self.user_answer == self.correct_answer:
#             return True
#         else:
#             return False
# 
# 
# class DosageActivityForm(forms.ModelForm):
#     class Meta:
#         model = DosageActivityBlock
# 
# 
#  
#  

