import os

from django.core.exceptions import ValidationError


def validate_document_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    # Supported extensions for document field.
    valid_extensions = ['.pdf', '.doc', '.docx', '.zip']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Недозволене розширення файлу')


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.odt', '.rtf', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Недоступне розширення файлу')
