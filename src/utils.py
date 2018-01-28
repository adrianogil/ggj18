from random import randint

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        pass
 
    return False

def get_random(l):
    '''
        list l
    '''
    return l[randint(0, len(l)-1)]