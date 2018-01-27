from random import randint

def get_random(l):
    '''
        list l
    '''
    return l[randint(0, len(l)-1)]