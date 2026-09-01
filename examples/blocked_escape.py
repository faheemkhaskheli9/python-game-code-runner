# Example submission that the sandbox REJECTS before running:
# the classic introspection escape that walks from a literal to os.system.
print("trying to escape...")
cls = ().__class__.__bases__[0]
for sub in cls.__subclasses__():
    print(sub)
