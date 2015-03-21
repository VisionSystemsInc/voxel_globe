import weakref

class Register(object):
  def __init__(self):
    Weak dictionary?
  
  def register(self, history):
    self.values.add(history)
    
  def unregister(self, history):
    self.values.remove(history)
    
  

  def getValues(self):
    values= [];
    for v in self.values:
      values.append(v.value)
    del v #MUST delete this, it's a strong ref
    return values 