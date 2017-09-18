
import string

from ..common import Status, FilterBase

def traverse(data, func):
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            ret[k] = traverse(v, func)
        return ret
    else:
        return func(data)

class Converter(FilterBase):
    def __init__(self, confs):
        super().__init__(confs['filtername'])
        self.typetemplate = confs.get('type', '{type}')
        self.datatemplate = confs.get('data', {})

    def onmessage(self, message):
        nm = self.convert(message)
        self.Q.put(nm)

    def convert(self, message):
        newtype = self.typetemplate.format(**message.to_dict())
        newdata = traverse(
            self.datatemplate,
            lambda t: t.format(**message.to_dict())
        )
        return Status(self.filtername, newtype, newdata)
