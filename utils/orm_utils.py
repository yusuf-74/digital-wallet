from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model, QuerySet
from django.db.models.fields.reverse_related import (
    ForeignObjectRel,
    ManyToManyRel,
    ManyToOneRel,
    OneToOneRel,
)
from rest_framework.request import Request


def is_path_contains_reverse_relation(model: Model, path: str) -> bool:
    current_model = model
    parts = path.split(".")

    for part in parts:
        try:
            field_obj = current_model._meta.get_field(part)
            if isinstance(field_obj, (ManyToManyRel, ForeignObjectRel, ManyToOneRel, OneToOneRel)):
                return True
            if hasattr(field_obj, 'related_model'):
                current_model = field_obj.related_model
            else:
                raise FieldDoesNotExist(f"Field '{part}' is not a valid relationship field.")
        except FieldDoesNotExist:
            raise FieldDoesNotExist(f"Field '{part}' is not a valid relationship field.")

    return False


def query_optimizer(model: Model, request: Request) -> QuerySet:
    expand = request.query_params.get('expand', None)
    fields = request.query_params.get('fields', None)
    queryset = model.objects.all()

    if expand:
        expand_fields = expand.split(',')
        select_related = set()
        prefetch_related = set()

        for field in expand_fields:
            try:
                is_reverse_or_many = is_path_contains_reverse_relation(model, field)
                if is_reverse_or_many:
                    prefetch_related.add(field.replace('.', '__'))
                else:
                    select_related.add(field.replace('.', '__'))
            except FieldDoesNotExist as e:
                print(f"Skipping invalid field: {str(e)}")
                continue

        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

    if fields:
        valid_fields = []
        field_list = fields.split(',')

        for field in field_list:
            field_parts = field.split('.')
            current_model = model
            is_valid = True

            for part in field_parts[:-1]:
                try:
                    field_obj = current_model._meta.get_field(part)
                    if hasattr(field_obj, 'related_model'):
                        current_model = field_obj.related_model
                    else:
                        is_valid = False
                        break
                except FieldDoesNotExist:
                    is_valid = False
                    break

            if is_valid:
                try:
                    current_model._meta.get_field(field_parts[-1])
                    valid_fields.append(field.replace('.', '__'))
                except FieldDoesNotExist:
                    pass

        if valid_fields:
            queryset = queryset.only(*valid_fields)

    return queryset
