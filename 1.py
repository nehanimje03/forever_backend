# sqrt
import math
def square_root(func):
    def wrapper(num):
        result = math.sqrt(num)
        return func(result)
    return wrapper

@square_root
def number(num):
    print('num is:',num)

number(25)


s = input("enter string:")

def reverse_string(s):
    rev = ''
    for i in s:
        rev = i + rev
    return rev

print(reverse_string(s))

nums = [10, 20, 20, 4, 45, 99]

a = list(set(nums))   # remove duplicates
a.remove(max(a))   # remove largest

print(max(a))         # second largest



l = [10,20,30,40,40,50]

def remove_duplicate(l):
    result = []
    for i in l:
        if i not in result:
            result.append(i)
    return result

print(remove_duplicate(l))


s = int(input("enter the number"))

def factorial(s):
    if s == 1:
        return 1
    return s*factorial(s-1)

print(factorial(s))



s = input("Enter String:")

def duplicate_string(s):
    seen = ''
    duplicate = ''

    for char in s:
        if char in seen:
            if char not in duplicate:
                duplicate += char
        else:
            seen += char
    return duplicate
    
print(duplicate_string(s))


def remove_duplicate_list(l):
    result =[]

    for i in l :
        if i not in result:
            result.append(i)

    return result

print(remove_duplicate_list([10,20,30,30]))

def remove_du_string(s):
    result = ''

    for i in s:
        if i not in result:
            result += i

    return result

print(remove_du_string('neeha'))

def find_duplicate_string(s):
    seen = ''
    duplicate = ''

    for i in s:
        if i in seen:
            if i not in duplicate:
                duplicate += i
        else:
            seen += i

    return duplicate

print(find_duplicate_string('neeha'))
            