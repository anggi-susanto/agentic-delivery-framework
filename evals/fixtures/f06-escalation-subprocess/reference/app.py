import subprocess
def run(a,c):
 if c(): raise RuntimeError("cancelled")
 if not isinstance(a,list) or not all(isinstance(x,str) for x in a): raise ValueError("argv")
 return subprocess.run(a,shell=False,capture_output=True,text=True,check=True).stdout
