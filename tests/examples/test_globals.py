global xyz
xyz=2106

def abc():
    global xyz
    xyz+=1
    print("Midst:",xyz)


print("Pre:",xyz)
abc()
print("Post:",xyz)
