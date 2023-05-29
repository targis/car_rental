from django.forms import FileInput, RadioSelect
from django.template.loader import render_to_string


class ImagePreviewWidget(FileInput):
    template_name = 'image_preview_widget.html'

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return render_to_string(self.template_name, context)


class StarRatingWidget(RadioSelect):
    template_name = 'star_rating_widget.html'
