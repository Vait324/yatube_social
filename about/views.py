from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'name': 'Павел Войтович',
            'git_adress': 'https://github.com/Vait324',
            'some_thoughts': 'Вдохновляющий текст о превозмогании и успехе'
        }
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tools'] = 'Visual Studio Code'
        return context
