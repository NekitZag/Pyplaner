from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponse


def render_logout(request):
    return redirect('/users/login/')


