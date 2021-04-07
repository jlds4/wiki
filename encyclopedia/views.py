from django.shortcuts import render
from random import randint, seed
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
import time

from markdown2 import Markdown

from . import util


class NewPageForm(forms.Form):
    title = forms.CharField(label="",)
    description = forms.CharField(label="", widget=forms.Textarea(attrs={"rows": 2, "cols": 10}))


class EditPageForm(forms.Form):
    def __init__(self, page):
        super().__init__()
        self.fields['description'] = forms.CharField(label="", widget=forms.Textarea(attrs={"rows": 2, "cols": 10}), initial=page)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):

    titleLower = title.lower()
    entries = util.list_entries()
    entriesLower = [i.lower() for i in entries]
    markdown = Markdown()

    if titleLower in entriesLower:
        with open('entries/' + title + '.md', 'r') as f:
            text = f.read()
            html = markdown.convert(text)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": html
        })
    else:
        return render(request, "encyclopedia/notfound.html", {
            "title": title,
        })


def search(request):
    search = request.GET.get('q').lower()
    results = []

    for entry in util.list_entries():
        entryLower = entry.lower()
        if search == entryLower:
            return HttpResponseRedirect(reverse("entry", kwargs={'title': entry}))
        if entryLower.count(search) > 0:  # checks if the search is a substring on any of the entries
            results.append(entry)
    return render(request, "encyclopedia/search.html", {
        "search": search,
        "results": results
    })


def random(request):
    entries = util.list_entries()
    seed(time.perf_counter())
    randomValue = randint(0, len(entries)-1)
    title = entries[randomValue]
    return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))


def newpage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            titleLower = title.lower()
            for entry in util.list_entries():
                entryLower = entry.lower()
                if titleLower == entryLower:
                    return render(request, "encyclopedia/newpage.html", {
                        "form": form,
                        "error": 1
                    })
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            util.save_entry(title, description)
            return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/newpage.html", {
                "form": form
            })
    else:
        return render(request, "encyclopedia/newpage.html", {
            "form": NewPageForm(),

        })


def edit(request, title):
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data["description"]
            util.save_entry(title, description)
            return HttpResponseRedirect(reverse("index"))
        else:
            description = request.POST.get('description', False)
            util.save_entry(title, description)
            return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
    else:
        page = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "form": EditPageForm(page),
            "title": title
        })

