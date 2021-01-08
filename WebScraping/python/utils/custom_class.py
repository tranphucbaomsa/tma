class CustomSwitcher(object):
    def numbers_to_months(self, argument):
        """Dispatch method"""
        method_name = 'month_' + str(argument)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda: "Invalid month")
        # Call the method as we return it
        return method()
 
    def month_1(self):
        return "January"
 
    def month_2(self):
        return "February"
 
    def month_3(self):
        return "March"

# class Example:
#     Variable = 2           # static variable

# print Example.Variable     # prints 2   (static variable)

# # Access through an instance
# instance = Example()
# print instance.Variable    # still 2  (ordinary variable)


# # Change within an instance 
# instance.Variable = 3      #(ordinary variable)
# print instance.Variable    # 3   (ordinary variable)
# print Example.Variable     # 2   (static variable)


# # Change through Class 
# Example.Variable = 5       #(static variable)
# print instance.Variable    # 3  (ordinary variable)
# print Example.Variable     # 5  (static variable)
