from django import forms
from log.custom_fields.customfield import CustomField
from django.forms import ValidationError
from django.utils.html import escape
from log.widgets import BBEditor
from postmarkup import render_bbcode
import HTMLParser

class TextField(forms.CharField, CustomField):
  def __init__(self, *args, **kwargs):
    super(TextField, self).__init__(widget=BBEditor, *args, **kwargs)

  def render(self, data):
    # FIXME dirty hack
    # we do this because cleditor performs escaping of html entities (<, >, &, ...)
    # as this is unreliable and unsafe anyway (since it's javascript and can be overwritten by the user)
    # and render_bbcode performs the same escaping, we need to unescape it first
    data = HTMLParser.HTMLParser().unescape(data)
    return render_bbcode(data)

class ShortTextField(forms.CharField, CustomField):
  def __init__(self, *args, **kwargs):
    super(ShortTextField, self).__init__(*args, **kwargs)

  def render(self, data):
    return escape(data)
