from django.core.paginator import Paginator

COUNT_PAGES = 10


def paginator_context(request, queryset):
    paginator = Paginator(queryset, COUNT_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
