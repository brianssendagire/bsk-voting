import json
import math
import os
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from .forms import OptionForm, RegisterForm, ResultsForm
from .utils import find_student, check_student_exists, populate_nominees, get_details, check_vote_status, check_nominee_status, check_nominee_validity, populate_results


def logout_view(request):
    logout(request)
    return redirect('home')


@method_decorator([never_cache], 'dispatch')
class HomeView(View):
    template_name = "options.html"

    # British School of Kampala
    def get(self, request, *args, **kwargs):
        context = {}
        form = OptionForm()
        context['option_form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = OptionForm(request.POST)
        context['option_form'] = form

        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            choice = form.cleaned_data['choice']

            # {"__all__": [{"message": "You need to choose a nominee from the dropdown list", "code": ""}]}
            if choice == 'Vote':
                if student_id:  # TODO flag if student_id is not provided
                    exists, name, status = find_student(student_id)
                    message = f'Dear {name}, we could not find your Student ID, please click <a href=''>here</a> to Register.'
                    if exists:
                        message = f"Welcome, {name}!"
                    return JsonResponse({'status': status, 'message': message})
        else:
            return JsonResponse({'status': 500, 'message': form.errors.as_json()})


@method_decorator([never_cache], 'dispatch')
class ResultsView(View):
    template_name = "results.html"

    def get(self, request, *args, **kwargs):
        context = {}
        form = ResultsForm(request.GET)
        context['filter_form'] = form
        context['title'] = 'Results'
        if form.is_valid():
            post = form.cleaned_data.get('post')
            if post:
                candidates = populate_results(post)
                context['candidates'] = candidates
                context['title'] = post.title()

        return render(request, self.template_name, context)


@method_decorator([never_cache], 'dispatch')
class RegisterView(View):
    template_name = "register.html"

    # British School of Kampala
    def get(self, request, *args, **kwargs):
        context = {}
        form = RegisterForm()
        context['register_form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = RegisterForm(request.POST)
        context['register_form'] = form

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            student_class = form.cleaned_data['student_class']
            student_house = form.cleaned_data['student_house']
            file_path = os.path.join(settings.STATIC_ROOT, 'files/STUDENTS.txt')
            exists, _id = check_student_exists(first_name.title(), last_name.title(), student_class, student_house)
            message = f"You are already registered with ID {_id}."
            if not exists:
                student_id = generate_id(first_name=first_name, last_name=last_name, house=student_house)
                with open(file_path, 'a') as f:
                    student = "\n" + student_id.upper() + "," + first_name.title() + "," + last_name.title() + "," + student_class + "," + student_house
                    f.write(student)
                message = f"You have registered with student ID {student_id.upper()}."
            messages.success(request, message)
            return redirect('home')
        return render(request, self.template_name, context)


# Function to generate student ID
def generate_id(**kwargs):
    f_name = kwargs['first_name'].upper()
    l_name = kwargs['last_name'].upper()
    house = kwargs['house'].upper()
    num = random.randint(0, 999)  # Generates random number between 0 and 1000 i.e. 0 is min and 999 is max

    digits = calculate_digits(num)
    _seq = f"0{num}" if digits == 2 else str(num)

    return '{}{}{}{}'.format(f_name[0], l_name[0], _seq, house[:2])


def calculate_digits(n): return int(math.log10(n)) + 1


def get_nominees(request):
    if request.method == 'POST':
        post = request.POST['post']
        student_id = request.POST['student_id']
        nominees = populate_nominees(post, student_id)
        return JsonResponse({'nominees': json.dumps(nominees)}, status=201)


def verify_id(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']

        if student_id:
            student_id = student_id.upper()
            exists, name, status = find_student(student_id)

            message = f"Welcome, {name}!"

            if not exists:
                message = f'Dear {name}, we could not find your Student ID, please click <a href=''>here</a> to Register.'
            return JsonResponse({'status': status, 'message': message, 'student_id': student_id})


def compute_option(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        choice = request.POST['choice']
        post = request.POST['post']
        vote_for = request.POST['vote_for']

        if choice == 'Vote':
            # choice, post, vote_for
            if not student_id:
                return JsonResponse({'status': 500, 'focus': 'student_id', 'message': 'You need to provide student ID'})
            if not post:
                return JsonResponse({'status': 500, 'focus': 'post', 'message': 'You need to select a Post'})
            if not vote_for:
                return JsonResponse({'status': 500, 'focus': 'vote_for', 'message': 'You need to choose your candidate from the dropdown List'})
            if student_id and post and vote_for:  # TODO flag if student_id is not provided
                exists, name, status = find_student(student_id)
                message = f"Welcome, {name}!"
                if not exists:
                    message = f"Dear {name}, we could not find your Student ID, please click <a href='/register'>here</a> to Register."
                    return JsonResponse({'status': 500, 'focus': 'student_id', 'message': message})
                """
                ## Algorithm
                1) Get details of student by ID
                2) Add details to voters
                3) Additional step to check if has voted for such post
                """
                voted = check_vote_status(student_id, post)
                if voted:
                    message = f"You already cast your vote for {post}, please choose a different post."
                    return JsonResponse({'status': 500, 'focus': 'post', 'message': message})
                _exists, student = get_details(student_id)
                if _exists and student:
                    file_path = os.path.join(settings.STATIC_ROOT, 'files/VOTERS.txt')
                    with open(file_path, 'a') as f:  # ID,position,Candidate ID,First Name,Last Name,Class,House
                        student = "\n" + student['id'] + "," + post + "," + vote_for + "," + student['first_name'].title() + "," + \
                                  student['last_name'].title() + "," + student['year'] + "," + student['house']
                        f.write(student)
                    message = f"You have voted {vote_for} for {post}. Thank you"
                return JsonResponse({'status': status, 'message': message})
        elif choice == 'Contest':
            if not student_id:
                return JsonResponse({'status': 500, 'focus': 'student_id', 'message': 'You need to provide student ID'})
            if not post:
                return JsonResponse({'status': 500, 'focus': 'post', 'message': 'You need to select a Post'})
            if student_id and post:
                exists, name, status = find_student(student_id)
                message = f"Welcome, {name}!"
                if not exists:
                    message = f"Dear {name}, we could not find your Student ID, please click <a href='/register'>here</a> to Register."
                    return JsonResponse({'status': 500, 'focus': 'student_id', 'message': message})
                eligible = check_nominee_validity(student_id, post)
                if not eligible:
                    message = f"You are not eligible to contest for {post}. Please try a different post"
                    return JsonResponse({'status': 500, 'focus': 'post', 'message': message})
                nominated, _post = check_nominee_status(student_id)
                if nominated:
                    message = f"You are already a nominee for {_post}. You can not sign up again."
                    return JsonResponse({'status': 500, 'focus': 'post', 'message': message})
                _exists, student = get_details(student_id)
                if _exists and student:
                    file_path = os.path.join(settings.STATIC_ROOT, 'files/NOMINEES.txt')
                    with open(file_path, 'a') as f:  # position,ID,First Name,Last Name,Class,House
                        student = "\n" + post + "," + student['id'] + "," + student['first_name'].title() + "," + \
                                  student['last_name'].title() + "," + student['year'] + "," + student['house']
                        f.write(student)
                    message = f"You have registered for {post}. Thank you"
                return JsonResponse({'status': status, 'message': message})


# FAQs
class FAQView(View):
    template_name = 'faqs.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)
