class CustomField:
  def __init__(self, user):
    self.user = user
    pass

  def format_value(self, value):
    return value

  def convert_value(self, value):
    return value

  def render(self, data):
    return "NOT YET IMPLEMENTED (data: %s)" % (data, )

