A={"draft":{"active"},"active":{"archived"},"archived":set()}
def transition(a,b):
 if b not in A.get(a,set()): raise ValueError("invalid")
 return b
