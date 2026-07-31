from urllib.parse import urlsplit
def approved_url(v):
 p=urlsplit(v)
 if p.scheme!="https" or p.hostname!="api.example.test" or p.username or p.password or p.fragment or p.port not in (None,443): raise ValueError("unapproved")
 return v
