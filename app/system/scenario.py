class Scenario:
  def __init__(self, sid):
    self.id = sid

  def __str__(self):
    return 'SID: ' + self.id

  def __repr__(self):
    return f'<SID: {self.id}>'
