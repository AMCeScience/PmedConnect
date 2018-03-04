import PmedConnect.config as config

class ParseFields(object):
  def __init__(self, default_parse_functions):
    self.available_fields = []
    self.add_functions(default_parse_functions)

  def add_functions(self, parse_functions):
    for name, parse_function in parse_functions.items():
      self.available_fields.append(name)

  def validate(self, fields = None):
    # If single field is passed, convert to list
    if type(fields) is not list and type(fields) is str:
      fields = [fields]

    # If nothing is passed return the default fields
    if fields is None:
      return self.available_fields
    
    # Get the differences between the fields passed into the function
    # and the list of available fields from the config
    unavailable_fields = set(fields) - set(self.available_fields)

    # Raise error when a field is not available
    if len(unavailable_fields) > 0:
      raise ValueError('Following fields do not have a parsing function: ' + ', '.join(map(str, unavailable_fields)))

    return fields