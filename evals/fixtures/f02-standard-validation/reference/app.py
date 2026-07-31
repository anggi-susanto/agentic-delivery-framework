def normalize_email(value):
 if not isinstance(value,str) or value.count("@")!=1: raise ValueError("invalid")
 a,b=value.strip().split("@")
 if not a or not b: raise ValueError("invalid")
 return a+"@"+b.lower()
