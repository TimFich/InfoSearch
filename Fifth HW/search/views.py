from django.http import HttpRequest
from django.shortcuts import render
from django import views

from search.searcher import query_searcher


class SearchPage(views.View):
    def get(self, request: HttpRequest):
        query = request.GET.get("q", None)
        files = []
        if query:
            files = query_searcher.search(query)
        return render(
            request,
            "search/main.html",
            context={
                "files": files,
                "query": query if query else "",
            },
        )
