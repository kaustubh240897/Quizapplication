from django.contrib import messages
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from ..decorators import teacher_required
from ..forms import TeacherSignUpForm
from ..models import Quiz, Question, PersonalDetails, OrganizationalDetails, Job, User, TakenJob
from django.http import HttpResponseRedirect

class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/recruiter-login.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'

        print(super().get_context_data(**kwargs))
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        print("*** check ******")
        print(self. model.username)
        login(self.request, user)
        messages.success(self.request, 'Successfully sign .')

        return redirect('teachers:add_organization')

@method_decorator([login_required, teacher_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/teachers/quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('subject') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        return queryset


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'subject', )
    template_name = 'classroom/teachers/quiz_add_form.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('teachers:quiz_change', quiz.pk)


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', 'subject', )
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('teachers:quiz_change', kwargs={'pk': self.object.pk})


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_delete_confirm.html'
    success_url = reverse_lazy('teachers:quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizResultsView(DetailView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'classroom/teachers/quiz_results.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('student__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


# @login_required
# @teacher_required
# def question_add(request, pk):
#     # By filtering the quiz by the url keyword argument `pk` and
#     # by the owner, which is the logged in user, we are protecting
#     # this view at the object-level. Meaning only the owner of
#     # quiz will be able to add questions to it.
#     quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)
#
#     if request.method == 'POST':
#         form = QuestionForm(request.POST)
#         if form.is_valid():
#             question = form.save(commit=False)
#             question.quiz = quiz
#             question.save()
#             messages.success(request, 'You may now add answers/options to the question.')
#             return redirect('teachers:question_change', quiz.pk, question.pk)
#     else:
#         form = QuestionForm()
#
#     return render(request, 'classroom/teachers/question_add_form.html', {'quiz': quiz, 'form': form})
#

# @login_required
# @teacher_required
# def question_change(request, quiz_pk, question_pk):
#     # Simlar to the `question_add` view, this view is also managing
#     # the permissions at object-level. By querying both `quiz` and
#     # `question` we are making sure only the owner of the quiz can
#     # change its details and also only questions that belongs to this
#     # specific quiz can be changed via this url (in cases where the
#     # user might have forged/player with the url params.
#     quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
#     question = get_object_or_404(Question, pk=question_pk, quiz=quiz)
#
#     AnswerFormSet = inlineformset_factory(
#         Question,  # parent model
#         Answer,  # base model
#         formset=BaseAnswerInlineFormSet,
#         fields=('text', 'is_correct'),
#         min_num=2,
#         validate_min=True,
#         max_num=10,
#         validate_max=True
#     )
#
#     if request.method == 'POST':
#         form = QuestionForm(request.POST, instance=question)
#         formset = AnswerFormSet(request.POST, instance=question)
#         if form.is_valid() and formset.is_valid():
#             with transaction.atomic():
#                 form.save()
#                 formset.save()
#             messages.success(request, 'Question and answers saved with success!')
#             return redirect('teachers:quiz_change', quiz.pk)
#     else:
#         form = QuestionForm(instance=question)
#         formset = AnswerFormSet(instance=question)
#
#     return render(request, 'classroom/teachers/question_change_form.html', {
#         'quiz': quiz,
#         'question': question,
#         'form': form,
#         'formset': formset
#     })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'classroom/teachers/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('teachers:quiz_change', kwargs={'pk': question.quiz_id})

## For Recruiter's Panel:
@method_decorator([login_required, teacher_required], name='dispatch')
class OrganizationDetailsView(CreateView):
    model = OrganizationalDetails
    fields = ('organization_name','organization_email','organization_description')
    template_name = 'classroom/teachers/organization_detail_form.html'

    def form_valid(self, form):
        organization_details = form.save(commit=False)
        check_user = OrganizationalDetails.objects.filter(user=self.request.user)

        if len(check_user)>=1:
            messages.error(self.request, 'Organizational Details Alredy Exist !!!')
        else:
            organization_details.user = self.request.user
            organization_details.save()
            messages.success(self.request, 'Added Organizational Details Successfully. ')
            
        #return HttpResponseRedirect("")
        return redirect('teachers:add_personal')

@method_decorator([login_required, teacher_required], name='dispatch')
class PersonalDetailsView(CreateView):
    model = PersonalDetails
    fields = ('first_name','last_name','email','mobile')
    template_name = 'classroom/teachers/personal_detail_form.html'
    context_object_name = 'personal'

    def form_valid(self, form):
        personal_details = form.save(commit=False)
        check_user = PersonalDetails.objects.filter(user=self.request.user)
        user_organization = OrganizationalDetails.objects.filter(user=self.request.user)

        if len(check_user)>=1:
            messages.error(self.request, 'already uploaded detail') 
        else:
            personal_details.user = self.request.user
            personal_details.organization = user_organization[0]
            personal_details.save()
            messages.success(self.request, 'Added Personal Details successfully !!!') 
        #return HttpResponseRedirect("")
        return redirect('teachers:post_job')
   
@method_decorator([login_required, teacher_required], name='dispatch')
class PostJobView(CreateView):
    model = Job
    fields = ('date_of_posting','offer','primary_profile','location','no_of_position','apply_deadline','drive_date','organization_sector','job_description','package',
                'required_skills','min_CPI','selection_process','other_details')
    template_name = 'classroom/teachers/post_job_form.html'

    def form_valid(self, form):
        job = form.save(commit=False)
        current_user = PersonalDetails.objects.filter(user=self.request.user)
        
        if len(current_user)==0:
            messages.error(self.request, 'Please Fill the Personal and Organizational Details ! !')
        else:
            job.user = self.request.user
            job.organization = current_user[0].organization
            job.save()
            messages.success(self.request, 'Added Job Successfully.')
        
        #return HttpResponseRedirect("")
        return redirect('teachers:my_jobs')

@method_decorator([login_required, teacher_required], name='dispatch')
class my_jobsView(ListView):
    model = Job
    template_name='classroom/teachers/quiz_change_list.html'
    context_object_name = 'jobs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['jobs'] = Job.objects.all().filter(user = self.request.user)
        print(context['jobs'])
        return context

# @method_decorator([login_required, teacher_required], name='dispatch')
# class ViewApplication(ListView):
#         model = TakenJob
#         template_name = 'classroom/teachers/view_application.html'
#         context_object_name = 'applied_job'

#         def get_context_data(self, **kwargs):
#             context = super().get_context_data(**kwargs)
#             context['applied_job'] = TakenJob.objects.all()
#             print(context['applied_job'])
#             return context

def view_application(request, pk):
    job = Job.objects.get(pk=pk)
    applicants = TakenJob.objects.filter(applied_job=job)
    return render(request, 'classroom/teachers/view_application.html',{'applicants': applicants})