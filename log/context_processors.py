from django.conf import settings

def development_processor(request):
  return {'DEVELOPMENT': settings.DEVELOPMENT}
