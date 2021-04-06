"""
抽象化的bootstrap类，用于对form字段的表单初始化
"""


class BootStrapForm(object):
    def __init__(self, *args, **kwargs):
        super(BootStrapForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = "请输入{}".format(field.label)
