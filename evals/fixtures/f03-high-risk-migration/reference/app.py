def apply(rows):
 for x in rows:
  if "status" not in x: x["status"]="pending"; x["_added"]=True
 return rows
def rollback(rows):
 for x in rows:
  if x.pop("_added",False): x.pop("status",None)
 return rows
