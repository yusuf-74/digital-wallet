from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        if hasattr(instance, 'last_updated_by'):
            validated_data['last_updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)

    def create(self, validated_data):
        if hasattr(self.Meta.model, 'last_updated_by'):
            validated_data['last_updated_by'] = self.context['request'].user
        return super().create(validated_data)

    def run_validation(self, data):
        mutable_data = data.copy()
        if hasattr(self.Meta.model, 'last_updated_by'):
            mutable_data['last_updated_by'] = int(self.context['request'].user.id)
        if hasattr(self.Meta.model, 'created_by'):
            mutable_data['created_by'] = int(self.context['request'].user.id)
        return super().run_validation(mutable_data)

    def _error_formatter(self, errors):
        formatted_errors = []
        for field, error in errors.items():
            for message in error:
                formatted_errors.append(
                    {
                        'field': field,
                        'message': message,
                    }
                )
        return {
            'success': False,
            'message': 'Validation failed',
            'errors': formatted_errors,
        }

    def is_valid(self, raise_exception=False):
        valid = super().is_valid(raise_exception=False)
        if not valid and raise_exception:
            raise serializers.ValidationError(self._error_formatter(self.errors))
        elif not valid:
            self._errors = self._error_formatter(self.errors)
        return valid


class BaseSerializer(serializers.Serializer):
    def _error_formatter(self, errors):
        formatted_errors = []
        for field, error in errors.items():
            for message in error:
                formatted_errors.append(
                    {
                        'field': field,
                        'message': message,
                    }
                )
        return {
            'success': False,
            'message': 'Validation failed',
            'errors': formatted_errors,
        }
