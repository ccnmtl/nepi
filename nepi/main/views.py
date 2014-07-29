'''Views for NEPI, should probably break up
into smaller pieces.'''
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from pagetree.generic.views import PageView, EditView, InstructorView
from pagetree.models import Hierarchy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.mail import send_mail, BadHeaderError
import json
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView, CreateView, \
    UpdateView
from django.views.generic.list import ListView
from nepi.activities.views import JSONResponseMixin
from nepi.main.forms import CreateAccountForm, ContactForm, \
    UpdateProfileForm, CreateGroupForm
from nepi.main.models import Group, UserProfile, Country, School, \
    PendingTeachers
from pagetree.generic.views import PageView, EditView, InstructorView
from pagetree.models import Hierarchy, UserPageVisit
import json


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class LoggedInMixinStaff(object):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinStaff, self).dispatch(*args, **kwargs)


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)


class ViewPage(LoggedInMixin, PageView):
    template_name = "main/page.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"
    gated = False

    def get_extra_context(self):
        menu = []
        visits = UserPageVisit.objects.filter(user=self.request.user,
                                              status='complete')
        visit_ids = visits.values_list('section__id', flat=True)

        previous_unlocked = True
        for section in self.root.get_descendants():
            unlocked = section.id in visit_ids
            item = {
                'id': section.id,
                'url': section.get_absolute_url(),
                'label': section.label,
                'depth': section.depth,
                'disabled': not(previous_unlocked or section.id in visit_ids)
            }
            menu.append(item)
            previous_unlocked = unlocked

        return {'menu': menu}


class EditPage(LoggedInMixinSuperuser, EditView):
    template_name = "main/edit_page.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"


# this is from default pagetree
class InstructorPage(LoggedInMixinStaff, InstructorView):
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"


class ThankYou(LoggedInMixin, View):

    def get(self, request):
        '''not entirely sure how thise will be called yet...
        need to determine how we will indicate what the situation is...'''
        if request.is_ajax():
            pass
#             if get
#             pk=self.request.POST.__getitem__('country'))

    def post(self, request):
        '''again not entirely sure how this is going to be called'''
        pass


def thanks_group(request, group_id):
    """Returns thanks for joining group page."""
    return render(request, 'student/thanks_group.html')


class Home(LoggedInMixin, View):
    '''redoing so that it simply redirects people where they need to be'''

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user.pk)
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect(reverse('register'))
        if user_profile.profile_type == 'ST':
            return HttpResponseRedirect(reverse('student-dashboard',
                                        kwargs={'pk': user_profile.pk}))
            # return HttpResponseRedirect(reverse('student-dashboard',
            #    {'pk' : profile.pk})) # {% url 'news-year-archive' yearvar %}"
        elif user_profile.profile_type == 'TE':
            return HttpResponseRedirect(reverse('faculty-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        elif user_profile.profile_type == 'IC':
            return HttpResponseRedirect(reverse('icap-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        else:
            '''I assume it could be possible another
            app has a profile_type variable?'''
            return HttpResponseRedirect(reverse('register'))


class StudentDashboard(LoggedInMixin, DetailView):
    '''For the first tab of the dashboard we are showing
    groups that the user belongs to, and if they do not belong to any
    we are giving the the option to affiliate with one'''
    model = UserProfile
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(StudentDashboard, self).get_context_data(**kwargs)
        context['modules'] = Hierarchy.objects.all()
        return context


class FacultyDashboard(StudentDashboard):
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_students_in_progress(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        in_progress = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                in_progress = in_progress + 1
        return in_progress

    def get_students_incomplete(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        incomplete = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                incomplete = incomplete + 1
            return incomplete

    def get_students_done(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        done = 0
        for each in find_students:
            if each.percent_complete() == 100:
                done = done + 1
        return done

    def get_context_data(self, **kwargs):
        context = super(FacultyDashboard, self).get_context_data(**kwargs)
        context['students'] = UserProfile.objects.filter(
            profile_type="ST").count()
        context['in_progress'] = self.get_students_in_progress()
        context['incomplete'] = self.get_students_done()
        context['done'] = self.get_students_incomplete()
        context['created_groups'] = Group.objects.filter(
            creator=User.objects.get(pk=self.request.user.pk))
        return context


class CountryAdminDashboard(FacultyDashboard):
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CountryAdminDashboard, self).get_context_data(**kwargs)
        # is this necessary? or can I just reference object/userprofile?
        profile = UserProfile.objects.get(user=self.request.user.pk)
        context['country'] = Country.objects.get(pk=profile.country.pk)
        # is this possible? guess we'll find out...
        context['country_schools'] = \
            School.objects.get(country=context['country'])
        return context


class ICAPDashboard(FacultyDashboard):
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ICAPDashboard, self).get_context_data(**kwargs)
        context['pending_teachers'] = PendingTeachers.objects.filter(
            user_profile__profile_type='TE')
        context['countries'] = Country.objects.all()
#             profile_type="ST").count()
#         context['in_progress'] = self.get_students_in_progress()
#         context['incomplete'] = self.get_students_done()
#         context['done'] = self.get_students_incomplete()
        # context['created_groups'] = Group.objects.filter(
        #     creator=User.objects.get(pk=self.request.user.pk))
        # context['joined_groups'] = UserProfile.objects.get(
        #     user=self.request.user.pk).group.all()
        # context['modules'] = Hierarchy.objects.all()
        return context


class GetReport(LoggedInMixin, View):
    template_name = 'dashboard.html'

    def post(self, request):
        if self.request.is_ajax():
            user_id = request.user.pk
            user_profile = UserProfile.objects.get(user=user_id)
            user_profile.country = Country.objects.get(
                pk=self.request.POST.__getitem__('country'))
            user_profile.school = School.objects.get(
                pk=self.request.POST.__getitem__('school'))
            user_profile.group = Group.objects.filter(
                pk=self.request.POST.__getitem__('group'))
            user_profile.save()
            return self.render_to_json_response(user_profile)
        else:
            return self.request


class JoinGroup(LoggedInMixin, JSONResponseMixin, View):
    template_name = 'dashboard/icap_dashboard.html'

    def post(self, request):
        user_id = request.user.pk
        user_profile = UserProfile.objects.get(user__id=user_id)
        add_group = Group.objects.get(pk=request.POST['group'])
        user_profile.group.add(add_group)
        for each in user_profile.group.all():
            print each.name
        return self.render_to_json_response({'success': True})


class GetCountries(LoggedInMixin, ListView):
    model = Country
    template_name = 'dashboard/country_list.html'
    success_url = '/'


class GetCountrySchools(LoggedInMixin, ListView):
    model = School
    template_name = 'dashboard/school_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            country_key = self.request.GET.__getitem__('name')
            country = Country.objects.get(pk=country_key)
            s = School.objects.filter(country=country)
            return {'school_list': s}


class GetSchoolGroups(LoggedInMixin, ListView):
    model = Group
    template_name = 'dashboard/group_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            school_key = self.request.GET.__getitem__('name')
            school = School.objects.get(pk=school_key)
            group_list = Group.objects.filter(school=school)
            return {'group_list': group_list}


class RegistrationView(FormView):
    '''changing registration view to form'''
    template_name = 'registration_form.html'
    form_class = CreateAccountForm
    success_url = '/account_created/'

    def register_user(self):
        pass

    def register_profile(self):
        pass

    def send_student_email(self):
        pass

    def send_teacher_notifiction(self):
        pass

    def form_valid(self, form):
        form_data = form.cleaned_data
        try:
            User.objects.get(username=form_data['username'])
            raise forms.ValidationError("this username already exists")
        except User.DoesNotExist:
            new_user = User.objects.create_user(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password1'])
            new_user.first_name = form_data['first_name']
            new_user.last_name = form_data['last_name']
            new_user.save()
            new_profile = UserProfile(user=new_user)
            new_profile.profile_type = 'ST'
            try:
                new_profile.country = Country.objects.get(
                    name=form_data['country'])
                new_profile.save()
            except Country.DoesNotExist:
                new_country = Country.objects.create(name=form_data['country'])
                new_country.save()
                new_profile.save()
            if form_data['email']:
                subject = "NEPI Registration"
                message = "Congratulations! " + \
                          "You've successfully registered to use NEPI.\n\n" + \
                          "Your user information is " + \
                          form_data['username'] + \
                          ".\n\n" + \
                          "You may now log in to your account."
                sender = "nepi@nepi.ccnmtl.columbia.edu"
                recipients = [form_data['email']]
                send_mail(subject, message, sender, recipients)
            recipients = ["nepi@nepi.ccnmtl.columbia.edu"]
            if form_data['profile_type']:
                subject = "[Teacher] Account Requested"
                message = form_data['first_name'] + \
                    " " + form_data['last_name'] + \
                    "has requested teacher status in "
                    # need to add country and schools here
                pending = PendingTeachers.objects.create(
                    user_profile=new_profile)
                pending.save()
                send_mail(subject, message, sender, recipients)
        return super(RegistrationView, self).form_valid(form)


class CreateSchoolView(LoggedInMixin, CreateView):
    '''generic class based view for
    adding a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


class UpdateSchoolView(LoggedInMixin, UpdateView):
    '''generic class based view for
    editing a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


# LoggedInMixin,


class CreateGroupView(LoggedInMixin, CreateView):
    '''generic class based view for
    creating a group'''
    model = Group
    form_class = CreateGroupForm
    template_name = 'dashboard/create_group.html'
    success_url = '/'

    def form_valid(self, request):
        f = CreateGroupForm(self.request.POST)
        new_group = f.save(commit=False)
        creator = User.objects.get(pk=self.request.user.pk)
        profile = UserProfile.objects.get(user=creator)
        school = School.objects.get(pk=profile.school.pk)
        new_group.creator = creator
        new_group.school = school
        new_group.save()
        # why do I need to return an HTTPResponse explicitly?
        # Should happen automatically no?
        return HttpResponseRedirect('/')


class AddGroup(LoggedInMixin, CreateView):
    '''generic class based view for
    creating a group'''
    model = Group
    form_class = CreateGroupForm
    template_name = 'dashboard/new_group.html'
    success_url = '/'

    def form_valid(self, request):
        f = CreateGroupForm(self.request.POST)
        new_group = f.save(commit=False)
        creator = User.objects.get(pk=self.request.user.pk)
        profile = UserProfile.objects.get(user=creator)
        school = School.objects.get(pk=profile.school.pk)
        new_group.creator = creator
        new_group.school = school
        new_group.save()
        # why do I need to return an HTTPResponse explicitly?
        # Should happen automatically no?
        return HttpResponseRedirect('/')


class UpdateGroupView(LoggedInMixin, UpdateView):
    '''generic class based view for
    editing a group'''
    model = Group
    template_name = 'dashboard/create_group.html'
    success_url = '/'
    form_class = CreateGroupForm


class GroupDetail(LoggedInMixin, DetailView):
    '''generic class based view for
    see group details - students etc'''
    model = Group
    template_name = 'dashboard/group_details.html'
    success_url = '/'

    def get_students_in_progress(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        in_progress = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                in_progress = in_progress + 1
        return in_progress

    def get_students_incomplete(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        incomplete = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                incomplete = incomplete + 1
            return incomplete

    def get_students_done(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        done = 0
        for each in find_students:
            if each.percent_complete() == 100:
                done = done + 1
        return done

    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        context['user_profile'] = UserProfile.objects.get(
            user=self.request.user.pk)
        context['students'] = self.object.userprofile_set.all()
        context['student_count'] = self.object.userprofile_set.all().count()
        context['in_progress'] = self.get_students_in_progress()
        context['incomplete'] = self.get_students_done()
        context['done'] = self.get_students_incomplete()
        return context


class RemoveStudent(LoggedInMixin, JSONResponseMixin, View):
    '''Remove the student from a course.'''
    def post(self, request):
        group = get_object_or_404(Group,
                                     pk=request.POST['group'])
        student = get_object_or_404(Student,
                                         pk=request.POST['student'])
        leave_group.userprofile_set.remove(student)
        return render_to_json_response({'success': True})
        


class LeaveGroup(LoggedInMixin, View):
    template_name = 'dashboard/icap_dashboard.html'

    def get(self, request, pk):
        user_profile = UserProfile.objects.get(user__id=request.user.pk)
        leave_group = Group.objects.get(pk=pk)
        leave_group.userprofile_set.remove(user_profile)
        return HttpResponseRedirect("/")


class ContactView(FormView):
    '''changed contact view function to
    generic class based view'''
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = '/email_sent/'

    def form_valid(self, form):
        '''should this be in the form instead?'''
        form_data = form.cleaned_data
        sender = form_data['sender'],
        subject = form_data['subject'],
        message = form_data['message'],
        recipients = ['nepi@nepi.ccnmtl.columbia.edu']
        # ["u'cdunlop@columbia.edu'"]
        send_mail(subject, message, sender, recipients)
        form.send_email(recipients)
        return super(ContactView, self).form_valid(form)

# send_mail('Subject', 'Message.', 'from@example.com',
#     ['john@example.com', 'jane@example.com'])
# def send_email(request):
#     subject = request.POST.get('subject', '')
#     message = request.POST.get('message', '')
#     from_email = request.POST.get('from_email', '')
#     if subject and message and from_email:
#         try:
#             send_mail(subject, message, from_email, ['admin@example.com'])
#         except BadHeaderError:
#             return HttpResponse('Invalid header found.')
#         return HttpResponseRedirect('/contact/thanks/')
#     else:
#         # In reality we'd use a form class
#         # to get proper validation errors.
#         return HttpResponse('Make sure all fields are entered and valid.')


class DeleteGroupView(LoggedInMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('home')

    def dispatch(self, *args, **kwargs):
        resp = super(DeleteGroupView, self).dispatch(*args, **kwargs)
        if self.request.is_ajax():
            response_data = {"result": "ok"}
            return HttpResponse(json.dumps(response_data),
                                content_type="application/json")
        else:
            # POST request (not ajax) will do a redirect to success_url
            return resp


class StudentClassStatView(LoggedInMixin, DetailView):
    '''This view is for students to see their progress,
    should be included in main base template.'''
    model = Group
    template_name = 'view_group_stats.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            module = self.group.__module
            user = User.objects.get(pk=self.request.user.pk)
            profile = UserProfile.objects.get(user=user)
            return {'module': module, 'user': user, 'profile': profile}


class UpdateProfileView(LoggedInMixin, UpdateView):
    model = UserProfile
    template_name = 'profile_tab.html'
    form_class = UpdateProfileForm
    success_url = '/'

    def form_valid(self, form):
        # response = super(UpdateProfileView, self).form_valid(form)
        form_data = form.cleaned_data
        if form_data['faculty_access']:
            subject = "Facutly Access Requeted"
            message = "The user, " + form_data['first_name'] + \
                " " + form_data['last_name'] + " from " + \
                form_data['country'] + " has requested faculty " + \
                "faculty access at " + form_data['school'] + ".\n\n"
            sender = "nepi@nepi.ccnmtl.columbia.edu"
            recipients = "cdunlop@columbia.edu"
            send_mail(subject, message, sender, recipients)
        # not clear to me what validation is done for you
        form_data.save()

    def form_invalid(self, form):
        response = super(UpdateProfileView, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response


class FacultyCountries(LoggedInMixin, ListView):
    model = Country
    template_name = 'faculty/country_list.html'
    success_url = '/'


class FacultyCountrySchools(LoggedInMixin, ListView):
    model = School
    template_name = 'faculty/school_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            country_key = self.request.GET.__getitem__('name')
            country = Country.objects.get(pk=country_key)
            s = School.objects.filter(country=country)
            return {'school_list': s}
