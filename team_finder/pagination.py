from django.core.paginator import Paginator

ITEMS_PER_PAGE = 12


def paginate(queryset, request, per_page=ITEMS_PER_PAGE):
    """Return (page_obj, pagination_query) for template links."""
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)
    pagination_query = query_params.urlencode()
    if pagination_query:
        pagination_query += "&"

    return page_obj, pagination_query
