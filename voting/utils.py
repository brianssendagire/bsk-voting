import os

from django.conf import settings

from .config import INELIGIBLE_FOR_HEAD_PREFECT, INELIGIBLE_FOR_DEPUTY, CANDIDATES


def find_student(student_id):
    exists, name = False, "Student"
    status = 404
    file_path = os.path.join(settings.STATIC_ROOT, 'files/STUDENTS.txt')
    with open(file_path, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf8').strip().split(',')
            if student_id == line[0]:
                exists = True
                name = f"{line[1]}".title()
                status = 200
                break
    return exists, name, status


def get_details(student_id):
    exists, name = False, "Student"
    student = {}
    file_path = os.path.join(settings.STATIC_ROOT, 'files/STUDENTS.txt')
    with open(file_path, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf8').strip().split(',')
            if student_id == line[0]:
                exists = True
                student['id'] = line[0]
                student['first_name'] = line[1]
                student['last_name'] = line[2]
                student['year'] = line[3]
                student['house'] = line[4]
                break
    return exists, student


def check_vote_status(student_id, post):
    voted, name = False, "Student"
    file_path = os.path.join(settings.STATIC_ROOT, 'files/VOTERS.txt')
    with open(file_path, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf8').strip().split(',')
            if student_id == line[0] and post == line[1]:
                voted = True
                break
    return voted


def check_nominee_validity(student_id, post):
    eligible = True
    file_path = os.path.join(settings.STATIC_ROOT, 'files/STUDENTS.txt')
    with open(file_path, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf8').strip().split(',')
            if student_id == line[0]:
                if line[3] in INELIGIBLE_FOR_HEAD_PREFECT and post in ['Head prefect', 'Head boy', 'Head girl']:
                    eligible = False
                elif line[3] in INELIGIBLE_FOR_DEPUTY and post in ['Deputy head boy', 'Deputy head girl']:
                    eligible = False
                elif line[3] in CANDIDATES:
                    eligible = False
                break
    return eligible


def check_nominee_status(student_id):
    nominated, _post = False, "Student"
    file_path = os.path.join(settings.STATIC_ROOT, 'files/NOMINEES.txt')

    with open(file_path, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf8').strip().split(',')
            if student_id == line[1]:
                nominated = True
                _post = line[0]
                break
    return nominated, _post


def check_student_exists(f_name, l_name, year, house):
    exists = False
    _id = None
    file_path = os.path.join(settings.STATIC_ROOT, 'files/STUDENTS.txt')
    with open(file_path, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf8').strip().split(',')
            try:
                if f_name == line[1] and l_name == line[2] and year == line[3] and house == line[4]:
                    exists = True
                    _id = line[0]
                    break
            except IndexError as e:
                pass
    return exists, _id


def populate_posts():
    file_path = os.path.join(settings.STATIC_ROOT, 'files/NOMINEES.txt')
    posts = ((None, 'Choose a post'),)
    with open(file_path, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf8').strip().split(',')
            post = line[0]
            _t = (post, post)
            if str(post).lower() != 'position' and _t not in posts:
                posts = (*posts, _t)
    return posts


"""
1) Interested in house of voter
2) Compare house of voter with house of house prefect
3) If post == 'House prefect' 
"""


def populate_nominees(post, student_id):
    file_path = os.path.join(settings.STATIC_ROOT, 'files/NOMINEES.txt')
    nominees = []
    exists, student = get_details(student_id)
    if exists:
        with open(file_path, 'rb') as f:
            for line in f.readlines():
                line = line.decode('utf8').strip().split(',')
                if post == line[0]:  # e.g. If selected post (Head prefect) == item at index 0 of Nominees file (the post)
                    _p = line[0]
                    student_id = line[1]
                    name = line[2] + ' ' + line[3]
                    if post == 'House prefect' and student['house'] == line[5]:
                        nominees.append({'id': student_id, 'name': name})
                    else:
                        nominees.append({'id': student_id, 'name': name})
    return nominees
