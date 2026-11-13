"""Validation bornee du texte libre et des images facultatives."""
import uuid
import warnings
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
from django.core.files.base import ContentFile
from rest_framework import serializers


class SafeProjectImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if getattr(data, 'size', 0) > 4 * 1024 * 1024:
            raise serializers.ValidationError('Une image ne doit pas depasser 4 Mo.')
        image_file = super().to_internal_value(data)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(image_file) as image:
                    if image.format not in ('JPEG', 'PNG', 'WEBP') or image.width * image.height > 12_000_000:
                        raise serializers.ValidationError('Image trop grande ou format non pris en charge.')
                    image = ImageOps.exif_transpose(image)
                    image.thumbnail((2400, 2400))
                    output = BytesIO()
                    # Reencoder retire le contenu annexe et les metadonnees EXIF.
                    image.convert('RGB').save(output, format='JPEG', quality=88)
            result = ContentFile(output.getvalue(), name=f'{uuid.uuid4().hex}.jpg')
            result.display_name = Path(str(data.name).replace('\\', '/')).name[:120]
            return result
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise serializers.ValidationError('Image invalide.')


class PresentationWriteSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=10000, allow_blank=True)
    problem = serializers.CharField(max_length=2000, allow_blank=True)
    base_updated_at = serializers.DateTimeField()
    images = serializers.ListField(child=SafeProjectImageField(), max_length=4, required=False, default=list)
    remove_image_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), max_length=4, required=False, default=list)


class PresentationSuggestionSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=10000, allow_blank=True)
    language = serializers.ChoiceField(choices=('fr', 'en'), default='fr')
