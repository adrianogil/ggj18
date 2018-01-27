import random

def is_num(s):
        return s == '0' or \
               s == '1' or \
               s == '2' or \
               s == '3' or \
               s == '4' or \
               s == '5' or \
               s == '6' or \
               s == '7' or \
               s == '8' or \
               s == '9'

class Dice:

    @staticmethod
    def dn(d,n):
        rand_result = 0
        for i in range(n):
            rand_result = rand_result + random.randint(1,d)
        return rand_result

    @staticmethod
    def d4(n):
        return dn(4,n)

    @staticmethod
    def parse(str_dice_data):
        current_value = 0
        current_num = 0
        current_num_dice = 0
        num_str = ''
        dice_str = ''

        waiting_for_dice = False

        for s in str_dice_data:
            if waiting_for_dice:
                dice_str = dice_str + s
            elif is_num(s):
                num_str = num_str + s
            elif s == 'd':
                current_num_dice = int(num_str)
                num_str = ''
                dice_str = '' 
                waiting_for_dice = True
        if dice_str != '':
            current_value = current_value + Dice.dn(int(dice_str), current_num_dice)
        if num_str != '':
            current_value = current_value + int(num_str)

        return current_value
