import filetype
import logging

from django.core.exceptions import ValidationError

from drf_extra_fields.fields import Base64FileField, Base64FieldMixin, FileField

logger = logging.getLogger(__name__)


class HybridFileField(Base64FileField):
    """
    A django-rest-framework field for handling file-uploads through
    raw post data, with a fallback to multipart form data.
    """

    ALLOWED_TYPES = map(lambda file_type: file_type.EXTENSION, filetype.types)

    def to_internal_value(self, data):
        """
        Try Base64Field first, and then try the FileField
        ``to_internal_value``, MRO doesn't work here because
        Base64FieldMixin throws before ImageField can run.
        """
        try:
            return Base64FieldMixin.to_internal_value(self, data)
        except ValidationError:
            return FileField.to_internal_value(self, data)

    def get_file_extension(self, filename, decoded_file):
        """Returns guessed extension of passed file."""
        extension = filetype.guess_extension(decoded_file)
        if extension is None:
            logger.error("Передан неизвестный тип файла")
        else:
            logger.info(f"Расширение файла: {extension}")
        return "jpg" if extension == "jpeg" else extension
