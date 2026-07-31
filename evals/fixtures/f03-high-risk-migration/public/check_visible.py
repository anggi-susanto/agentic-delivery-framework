from app import apply,rollback
r=[{}, {"status":"paid"}]
assert rollback(apply(r))==[{}, {"status":"paid"}]
