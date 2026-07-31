from app import run
assert run(["python3","-c","print(7)"],lambda:False).strip()=="7"
