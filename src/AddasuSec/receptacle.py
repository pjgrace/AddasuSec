from collections.abc import ValuesView


class Receptacle:
    def __init__(self, id):
        self.iid = id
        self._Comp = None
        self.m_connID = -1
        self.meta_Data = {}

    def connect(self, pIUnkSink, riid):
        if(riid!=self.iid):
            return False
        self._Comp = pIUnkSink
        return True

    def disconnect(self, id):
        if(id!=self.m_connID):
            return False
        self._Comp = None
        return True

    def putData(self, name, value):
        self.meta_Data.update([name, value])

    def getValue(self, name):
      return self.meta_Data.get(name)

    def getValues(self):
      return self.meta_Data.keys
        