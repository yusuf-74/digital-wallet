from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response


class UnifiedResponseMixin:
    """
    Mixin to format responses for all views, providing a consistent
    API structure with 'success', 'message', 'data', and 'errors' fields.
    """

    def format_response(self, response, success_message, error_message):
        is_success = response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_202_ACCEPTED,
        ]
        response.data = {
            'success': is_success,
            'message': success_message if is_success else error_message,
            'data': response.data if is_success else None,
            'errors': response.data if not is_success else None,
        }
        return response


class UnifiedResponseListAPIView(UnifiedResponseMixin, ListAPIView):
    list_success_message = 'Data retrieved successfully'
    list_error_message = 'Failed to retrieve data'

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.list_success_message, error_message=self.list_error_message
        )


class UnifiedResponseCreateAPIView(UnifiedResponseMixin, CreateAPIView):
    create_success_message = 'Created successfully'
    create_error_message = 'Failed to create'

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return self.format_response(
                response, success_message=self.create_success_message, error_message=self.create_error_message
            )
        except ValidationError:
            return Response(
                {"success": False, "message": "Validation Faild", "errors": serializer._errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_serializer(self, *args, **kwargs):
        data = self.request.data
        if isinstance(data, list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class UnifiedResponseRetrieveAPIView(UnifiedResponseMixin, RetrieveAPIView):
    retrieve_success_message = 'Data retrieved successfully'
    retrieve_error_message = 'Failed to retrieve data'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.retrieve_success_message, error_message=self.retrieve_error_message
        )


class UnifiedResponseUpdateAPIView(UnifiedResponseMixin, UpdateAPIView):
    update_success_message = 'Updated successfully'
    update_error_message = 'Failed to update'

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            response = Response(serializer.data)
            return self.format_response(
                response, success_message=self.update_success_message, error_message=self.update_error_message
            )
        except ValidationError:
            return Response(
                {"success": False, "message": "Validation Faild", "errors": serializer._errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_serializer(self, *args, **kwargs):
        data = self.request.data
        if isinstance(data, list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class UnifiedResponseDestroyAPIView(UnifiedResponseMixin, DestroyAPIView):
    destroy_success_message = 'Deleted successfully'
    destroy_error_message = 'Failed to delete'

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.destroy_success_message, error_message=self.destroy_error_message
        )


class UnifiedResponseListCreateAPIView(UnifiedResponseMixin, ListCreateAPIView):
    list_success_message = 'Data retrieved successfully'
    create_success_message = 'Created successfully'
    list_error_message = 'Failed to retrieve data'
    create_error_message = 'Failed to create'

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.list_success_message, error_message=self.list_error_message
        )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return self.format_response(
                response, success_message=self.create_success_message, error_message=self.create_error_message
            )
        except ValidationError:
            return Response(
                {"success": False, "message": "Validation Faild", "errors": serializer._errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_serializer(self, *args, **kwargs):
        data = self.request.data
        if isinstance(data, list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class UnifiedResponseRetrieveUpdateAPIView(UnifiedResponseMixin, RetrieveUpdateAPIView):
    retrieve_success_message = 'Data retrieved successfully'
    update_success_message = 'Updated successfully'
    retrieve_error_message = 'Failed to retrieve data'
    update_error_message = 'Failed to update'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.retrieve_success_message, error_message=self.retrieve_error_message
        )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            response = Response(serializer.data)
            return self.format_response(
                response, success_message=self.update_success_message, error_message=self.update_error_message
            )
        except ValidationError:
            return Response(
                {"success": False, "message": "Validation Faild", "errors": serializer._errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_serializer(self, *args, **kwargs):
        data = self.request.data
        if isinstance(data, list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class UnifiedResponseRetrieveDestroyAPIView(UnifiedResponseMixin, RetrieveDestroyAPIView):
    retrieve_success_message = 'Data retrieved successfully'
    destroy_success_message = 'Deleted successfully'
    retrieve_error_message = 'Failed to retrieve data'
    destroy_error_message = 'Failed to delete'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.retrieve_success_message, error_message=self.retrieve_error_message
        )

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.destroy_success_message, error_message=self.destroy_error_message
        )


class UnifiedResponseRetrieveUpdateDestroyAPIView(UnifiedResponseMixin, RetrieveUpdateDestroyAPIView):
    retrieve_success_message = 'Data retrieved successfully'
    update_success_message = 'Updated successfully'
    destroy_success_message = 'Deleted successfully'
    retrieve_error_message = 'Failed to retrieve data'
    update_error_message = 'Failed to update'
    destroy_error_message = 'Failed to delete'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.retrieve_success_message, error_message=self.retrieve_error_message
        )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            response = Response(serializer.data)
            return self.format_response(
                response, success_message=self.update_success_message, error_message=self.update_error_message
            )
        except ValidationError:
            return Response(
                {"success": False, "message": "Validation Faild", "errors": serializer._errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return self.format_response(
            response, success_message=self.destroy_success_message, error_message=self.destroy_error_message
        )

    def get_serializer(self, *args, **kwargs):
        data = self.request.data
        if isinstance(data, list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
