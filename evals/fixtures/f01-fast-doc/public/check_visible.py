from app import solve
solve()
assert open("completion.md").read()=="status: complete\n"
