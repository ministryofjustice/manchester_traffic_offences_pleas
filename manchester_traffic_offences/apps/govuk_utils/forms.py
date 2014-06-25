from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import NumberInput

class GovUkDateWidget(SelectDateWidget):
    """
    Same as SelectDateWidget, but uses NumberInput rather than Select.
    """
    def create_select(self, name, field, value, val, choices):
            if 'id' in self.attrs:
                id_ = self.attrs['id']
            else:
                id_ = 'id_%s' % name
            if not self.is_required:
                choices.insert(0, none_value)
            local_attrs = self.build_attrs(id=field % id_)
            s = NumberInput()
            select_html = s.render(field % name, val, local_attrs)
            return select_html