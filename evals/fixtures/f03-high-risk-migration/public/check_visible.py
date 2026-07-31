from app import apply
r=[{}, {"status":"paid"}]
apply(r)
assert r[0]["status"] == "pending"
assert r[1]["status"] == "paid"
