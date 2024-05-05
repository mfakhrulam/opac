class PaginateObj:

  """ Pagination dummy object. Takes a list and paginates it similar to sqlalchemy paginate() """
  def __init__(self, paginatable, page, per_page):
    self.has_next = (len(paginatable)/per_page) > page
    self.has_prev = bool(page - 1)
    self.next = page + self.has_next
    self.prev = page - self.has_prev
    self.items = paginatable[(page-1)*(per_page):(page)*(per_page)]
  
  # def __iter__(self):
  #   return iter(self.items)
  
  # def __next__(self): 
  #   self.current += 1
  #   if self.current < self.high:
  #     return self.current
  #   raise StopIteration