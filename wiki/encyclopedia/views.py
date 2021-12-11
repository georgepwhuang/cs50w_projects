from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.contrib import messages
from django.utils.safestring import mark_safe

from . import util

import random
import markdown2


class SearchForm(forms.Form):
    search = forms.CharField(label='',
                             widget=forms.TextInput(attrs={'class': "search", 'type': "text", 'name': "q",
                                                           'placeholder': 'Search Encyclopedia'}))


class NewForm(forms.Form):
    title = forms.CharField(label='',
                            widget=forms.TextInput(attrs={'placeholder': 'Input Title'}))
    content = forms.CharField(label='',
                              widget=forms.Textarea(attrs={'placeholder': 'Input Content'}))


class EditForm(forms.Form):
    content = forms.CharField(label='',
                              widget=forms.Textarea(attrs={'placeholder': 'Input Content'}))


def index(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["search"]
            return redirect(f"{reverse(index)}?{urlencode({'q': query})}")
    elif request.method == "GET":
        if request.GET.get("q"):
            query = request.GET.get("q")
            results = []
            for title in util.list_entries():
                if query.lower() == title.lower():
                    return page(request, title)
                elif query.lower() in title.lower():
                    results.append(title)
            return render(request, "encyclopedia/search.html", {
                "query": query,
                "entries": results,
                "search": SearchForm()
            })
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries(),
                "search": SearchForm()
            })


def page(request, title):
    entry = util.get_entry(title)
    if entry is None:
        return render(request, "encyclopedia/notfound.html", {
            "search": SearchForm()
        })
    else:
        return render(request, "encyclopedia/page.html", {
            "title": title,
            "entry": mark_safe(markdown2.markdown(entry)),
            "search": SearchForm(),
            "edit": reverse('edit', args=[title])
        })


def new(request):
    if request.method == "POST":
        form = NewForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in util.list_entries():
                messages.warning(request, 'This page already exists')
                return render(request, "encyclopedia/new.html", {
                    "search": SearchForm(),
                    "add": NewForm(request.POST)
                })
            else:
                edited_content = f"#{title}\n\n{content}"
                util.save_entry(title, edited_content)
                return redirect(reverse('page', args=[title]))
    else:
        return render(request, "encyclopedia/new.html", {
            "search": SearchForm(),
            "add": NewForm()
        })


def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect(reverse('page', args=[title]))
    else:
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "search": SearchForm(),
            "edit": EditForm(initial={"content": util.get_entry(title)})
        })


def rand(request):
    pages = util.list_entries()
    title = random.choice(pages)
    return redirect(reverse('page', args=[title]))
