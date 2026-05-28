# # import time

# # def timer(func):
# #     def warpper():
# #         start = time.time()
# #         func()
# #         end = time.time()
# #         print("time_taken: ", end - start)
# #     return warpper

# # @timer
# # def slow_func():
# #     time.sleep(1)
# #     print("slow_func")

# # slow_func()


# # # check even odd

# # def check_even_odd_num(func):
# #     def wrapper(num):
# #         if num % 2 == 0:
# #             print('even')
# #         else:
# #             print('odd')
# #         func(num)
# #     return wrapper


# # @check_even_odd_num
# # def check_number(num):
# #     print("number is:",num)

# # check_number(5)



# # # saure of number

# # def square_number(func):
# #     def wrapper(num):
# #         r = num*num
# #         return func(r)
    
# #     return wrapper

# # @square_number
# # def s_number(num):
# #     print("square of num is:",num)

# # s_number(2)

# # # root of number

# # # import math
# # # def root_number(func):
# # #     def wrapper(num):
# # #         r = math.sqrt(num)
# # #         return func(r)
# # #     return wrapper

# # # @root_number
# # # def r_number(num):
# # #     print("root of number:",num)

# # # r_number(25)

# # def check_positive_negative(func):
# #     def wrapper(num):
# #         if num > 0 :
# #             print("positive")
# #         else:
# #             print("negative")
# #         return func(num)
# #     return wrapper

# # @check_positive_negative
# # def p_n_number(num):
# #     print("number is:",num)

# # p_n_number(55)


# # # l =[1.2,3,4,5]

# # # def list_maise_odd_num_find(func):
# # #     def wrapper(l):
# # #         return func([i for i in l if i%2!=0 ])
# # #     return wrapper

# # # @list_maise_odd_num_find
# # # def odd_number(l):
# # #     print("odd number is",l)


# # # odd_number()



# # num = [10,20,30,40,50]
# # x1 = [x**2 for x in num]
# # print(x1)


# # n = [1,2,3,4]
# # a = [i**2 for i in num]
# # print(a)

# # l = [1,2,3,4,5]
# # na = [i for i in l if i%2==0]
# # print(na)

# # l = [1,2,3,4,5]
# # a = [i for i in l if i%2!=0]
# # print(a)


# # names = ['neha','krisha']
# # a = [i.upper() for i in names]
# # print(a)


# # l = [1,2,3,4,5]
# # a = ['even' if i%2==0 else 'odd' for i in l]
# # print(a)


# # l = [11,2,13,4,15]
# # a = ['even' if i%2==0 else 'odd' for i in l]
# # print(a)

# # d = ['n','','e','']
# # a = [i for i in d if i!='']
# # print(a)

# # l = [10,20,30,40]
# # a = [x**2 for x in l]
# # print(a)
# # #  


# # # n>10

# # l = [2,4,15,19,20]
# # c = [x for x in l if x>10]
# # print(c)

# # l = ['neha','nimje']
# # a = [len(i) for i in l]
# # print(a)

# # l = ['n','nr','neha']
# # w = [len(i) for i in l]
# # print(w)


# # d = {'d':1,"a":10,'b':2}
# # key = [k for k in d]
# # value = [v for v in d.values()]
# # print(key)
# # print(value)



# # # l = [1,2,3,4,5,6]

# # # a = [i for i in l if i%2==0]
# # # odd = [i for i in l if i%2!=0]
# # # print(a)
# # # print(odd)

# # nums = [10,20,30,40,40]

# # def dulicate_remove(nums):
# #     result = []

# #     for i in nums:
# #         if i not in result:
# #             result.append(i)

# #     return result

# # print(dulicate_remove(nums))

# # s = 'neha'
# # def reverse_string(s):
# #     rev = ''
# #     for i in s:
# #         rev = i + rev
# #     return rev

# # print(reverse_string(s))

# # a = s[::-1]
# # print(a)

# #  prime number : 2 no divide hota hai , 1 se or khud apne aap se 

# def is_prime(n):
#     if n<=2:
#         return False
    
#     for i in range(2,int(n**0.5)+1):
#         if n%i==0:
#             return False
#     return True

# print(is_prime(4))

# # a= int(input("enter no:"))

# # for i in range(a,0,-1):
# #     print("*"*i)

# # n = int(input("no:"))
# # for i in range(n,0,-1):
# #     print(" "*(n-i)+"*"*i)

# n=5
# for i in range(1,n+1):
#     print(" "*(n-i)+"*"*(2*i-1))


nums = [10, 20, 4, 45, 99]

# first = nums[0]
# second = nums[0]

s = "python"
rev = ""

for char in s:
    rev = char + rev