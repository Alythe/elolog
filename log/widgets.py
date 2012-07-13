# taken from http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/

from django import forms
from django.db import models
from django.template.loader import render_to_string
from django.forms.widgets import Select, MultiWidget, DateInput, TimeInput, TextInput, Textarea
from django.conf import settings
from time import strftime
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils import timezone
import datetime

class LogSplitDateTimeWidget(MultiWidget):

  def __init__(self, attrs=None, date_format='%d.%m.%Y', time_format='%H:%M', initial=None):
    date_class = attrs['date_class']
    time_class = attrs['time_class']
    del attrs['date_class']
    del attrs['time_class']

    time1_attrs = attrs.copy()
    time1_attrs['class'] = time_class
    time2_attrs = attrs.copy()
    time2_attrs['class'] = time_class

    self.date_format = date_format
    self.time_format = time_format

    date_attrs = attrs.copy()
    date_attrs['class'] = date_class
    date_attrs['readonly'] = 'true'

    # yuck. maybe rewrite the js routine to take real date format strings
    datepicker_format = date_format.replace('%d', 'dd').replace('%m', 'mm').replace('%Y', 'yyyy')
    date_attrs['data-date-format'] = datepicker_format

    if initial:
      date, hour, minute = self.decompress(initial)
      date_attrs['data_date'] = date
      date_attrs['value'] = date

      time1_attrs['value'] = hour
      time2_attrs['value'] = minute

    widgets = (DateInput(attrs=date_attrs, format=date_format),
               TimeInput(attrs=time1_attrs, format=time_format),
               TimeInput(attrs=time2_attrs, format=time_format),
               )

    super(LogSplitDateTimeWidget, self).__init__(widgets, attrs)

  def set_date_time_format(self, date_format, time_format):
    self.date_format = date_format
    self.time_format = time_format
    self.widgets[0].format = date_format
    self.widgets[1].format = time_format
    self.widgets[2].format = time_format

  def decompress(self, value):
    if value:
      d       = strftime(self.date_format,  value.timetuple())
      hour    = strftime("%H",              value.timetuple())
      minute  = strftime("%M",              value.timetuple())
      return (d, hour, minute)
    else:
      return (None, None, None)

  def format_output(self, rendered_widgets):
      return "%s %s:%s" % (rendered_widgets[0], rendered_widgets[1],
                                              rendered_widgets[2])

  class Media:
      css = {
            "all": (
              "css/datepicker.css",
              )
            }
      js = (
          "js/bootstrap-datepicker.js",
          "js/datepicker-init.js",
          )
      less = (
          "less/datepicker.less",
          )

class KDAWidget(MultiWidget):
  def __init__(self, attrs=None, initial=None):
    k_attrs = {}
    d_attrs = {}
    a_attrs = {}
    
    if attrs:
      k_attrs = attrs.copy()
      d_attrs = attrs.copy()
      a_attrs = attrs.copy()

    if initial:
      k, d, a = self.decompress(initial)
      k_attrs['value'] = k
      d_attrs['value'] = d
      a_attrs['value'] = a

    widgets = (TextInput(attrs=k_attrs),
               TextInput(attrs=d_attrs),
               TextInput(attrs=a_attrs))

    super(KDAWidget, self).__init__(widgets, attrs)

  def decompress(self, value):
    if value:
      data = value.split('/') 
      if len(data) == 3:
        return (data[0], data[1], data[2])
      else:
        return ("0", "0", "0")
    else:
      return ("0", "0", "0")

class BBEditor(Textarea):
  def __init__(self, attrs=None, initial=None, *args, **kwargs):
    super(BBEditor, self).__init__(*args, **kwargs)

  def render(self, name, value, attrs={}):
    if value is None:
      value = ''
    
    final_attrs = self.build_attrs(attrs, name=name)
    return mark_safe(u'''<textarea{flat_attrs}>{value}</textarea>
      <script type="text/javascript">
      $(function() {{
      $("#{id}").cleditor({{ controls: "bold italic underline strikethrough | bullets numbering | undo redo | | cut copy paste pastetext | source", useCSS: false }});
      }})
      </script>'''.format(
            flat_attrs=flatatt(final_attrs),
            value=value,
            id=final_attrs.get('id'),
        ))


  class Media:
    css = {
        "all": (
          "cleditor/jquery.cleditor.css",
          )
        }
    js = (
          "cleditor/jquery.cleditor.js",
          "cleditor/jquery.cleditor.bbcode.min.js",
        )

