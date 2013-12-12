'''
Created on Mar 8, 2013

@author: Daniel
'''
def list_to_number(li):
    # what this does is convert each element of a list of binary digits to a string,
    # then join them, then convert them to a decimal number.
    if len(li) > 1:
        return int(reduce(lambda x,y: str(x)+str(y), li), 2)
    elif len(li) == 1:
        return int(str(li[0]), 2)
    else:
        print len(li)
        raise Exception
    
def weighted_choice(weights):
    from random import random
    
    rnd = random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i