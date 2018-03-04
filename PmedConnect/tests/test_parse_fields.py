from unittest import TestCase

import PmedConnect.ParseFields as pf
import PmedConnect.config as config

class TestParseFields(TestCase):

  @classmethod
  def setUpClass(cls):
    parse_functions = {
      'test': '',
      'test2': ''
    }

    cls.fields_class = pf.ParseFields(parse_functions)

  def test_empty_fields_list(self):
    s = self.fields_class.validate()

    self.assertTrue(s == ['test', 'test2'])

  def test_single_field(self):
    s = self.fields_class.validate('test')

    self.assertTrue(s == ['test'])

  def test_filled_fields_list(self):
    s = self.fields_class.validate(['test', 'test2'])

    self.assertTrue(s == ['test', 'test2'])

  def test_unavailable_field(self):
    with self.assertRaises(ValueError):
      s = self.fields_class.validate('I_AM_NOT_AVAILABLE_AND_NEVER_WILL_BE')

  def test_unavailable_field_in_list(self):
    fields = ['test', 'test2', 'I_AM_NOT_AVAILABLE_AND_NEVER_WILL_BE']
    
    with self.assertRaises(ValueError):
      s = self.fields_class.validate(fields)