from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    page_size_query_param = 'page_size'
    """ Custom Paginator to handle returning all queryset """

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = self.get_page_size(request)
        if request.GET.get('page') == '*':
            self.page_size = len(queryset) if len(queryset) > 0 else 1
            request.GET._mutable = True
            request.GET['page'] = 1
        return super().paginate_queryset(queryset, request, view)
