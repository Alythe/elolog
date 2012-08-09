from django.template import Library
from django.utils.safestring import mark_safe
from postmarkup import render_bbcode
import HTMLParser

register = Library()

@register.filter
def render_bb( text ):
  if text.strip() != "":
    return mark_safe(render_bbcode(HTMLParser.HTMLParser().unescape(text)))
  else:
    return ""
