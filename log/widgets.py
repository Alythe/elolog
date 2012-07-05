# taken from http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/

from django import forms
from django.db import models
from django.template.loader import render_to_string
from django.forms.widgets import Select, MultiWidget, DateInput, TimeInput
from django.conf import settings
from time import strftime

class LogSplitDateTimeWidget(MultiWidget):

    def __init__(self, attrs=None, date_format=None, time_format=None, initial=None):
        date_class = attrs['date_class']
        time_class = attrs['time_class']
        del attrs['date_class']
        del attrs['time_class']

        time1_attrs = attrs.copy()
        time1_attrs['class'] = time_class
        time2_attrs = attrs.copy()
        time2_attrs['class'] = time_class

        date_attrs = attrs.copy()
        date_attrs['class'] = date_class
        date_attrs['data-date-format'] = settings.DATEPICKER_FORMAT

        if initial != None:
          date, hour, minute = self.decompress(initial)
          date_attrs['data_date'] = date
          date_attrs['value'] = date

          time1_attrs['value'] = hour
          time2_attrs['value'] = minute
        
        widgets = (DateInput(attrs=date_attrs, format=date_format),
                   TimeInput(attrs=time1_attrs, format=time_format), TimeInput(attrs=time2_attrs, format=time_format),
                   )

        super(LogSplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = strftime(settings.DATE_FORMAT, value.timetuple())
            hour = strftime("%H", value.timetuple())
            minute = strftime("%M", value.timetuple())
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

