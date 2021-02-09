#!/usr/bin/env python3
"""6.009 Lab 9: Snek Interpreter"""

import doctest
# NO ADDITIONAL IMPORTS!


###########################
# Snek-related Exceptions #
###########################

class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    pass


############################
# Tokenization and Parsing #
############################


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """  
    
    token = []
    comment = False
    for character in source:
        #if its a comment and isn't going to a new line, don't add it
        if not comment or character == "\n":
            #add spaces around the ( )
            if character == "(" or character == ")":
                token.append(" ")
                token.append(character)
                token.append(" ")
            elif character == ";":
                comment = True
            #new lines can be appended, they will just later be removed when join and split
            elif character == "\n":
                token.append(character)
                comment = False
            else:
                token.append(character)

    return "".join(token).split()
    
def checkLambdasSyntax(parsed):
    '''checks the syntax of the user made functions and definitions'''
    
    #if it is not a list, it doesn't have to be checked
    if type(parsed) == list:
        #checks for define syntax
        
        if len(parsed) > 0 and parsed[0] == 'define':
                if len(parsed) != 3:
                    raise SnekSyntaxError("Syntax error")
                #if the element after define is a list, that means that it should be turned into a function
                if type(parsed[1]) == list:
                    if parsed[1] == []:
                        raise SnekSyntaxError("Syntax Error")
                    parsed = ['define', parsed[1][0], ['lambda', parsed[1][1:], parsed[2]]]
                    checkLambdasSyntax(parsed)
                
                #give an error if element after define is a number
                elif type(parsed[1]) == int or type(parsed[1]) == float:
                    raise SnekSyntaxError("Syntax Error")
                    
        #checks the lambda syntax           
        elif len(parsed) > 0 and parsed[0] == 'lambda':
            if len(parsed) != 3 or type(parsed[1]) == int or type(parsed[1]) == float:
                raise SnekSyntaxError("Syntax Error")
                
                #checks that none of the parameters are numbers
            if type(parsed[1]) == list:
                for t in parsed[1]:
                    if type(t) == float or type(t) == int:
                        raise SnekSyntaxError("Syntax error")
        
        #if there are any lists inside that list, also check those lists for the
        #define and lambda syntax
        for i in range(len(parsed)):
            if type(parsed[i]) == list:
                checkLambdasSyntax(parsed[i])

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    #checks to see if all the parenthesis are being matched
    counting = 0
    for ch in tokens:
        if ch == '(':
            counting +=1
        elif ch == ')':
            counting -= 1
        if counting < 0:
            raise SnekSyntaxError("Syntax error - wrong parenthesis count")
    if counting != 0:
        raise SnekSyntaxError("Syntax error - wrong parenthesis count")
    
        
        
    def parse_parenthesis(index):
        '''
        A helper function to help parse that will occur recursively
        '''
        #try to transform them into actual numbers if they are strings of numbers
        try: 
            return int(tokens[index]), index +1   
        except:
            try: 
                return float(tokens[index]), index +1   
            except:
                
                #if there is a parenthesis, add a list
                if tokens[index] == '(':
                    adding = []
                    index += 1
                    while tokens[index] != ')':
                        changer, index = parse_parenthesis(index)
                        adding.append(changer)
                    return adding, index+1
                
                #if it gets here, its because it is just a simple string
                else:
                    return tokens[index], index +1
            
    parsed_parenthesis, next_index = parse_parenthesis(0)
    if next_index != len(tokens) and tokens[next_index] != ')':
        raise SnekSyntaxError("Syntax error - weird length")
    checkLambdasSyntax(parsed_parenthesis)
    
    return parsed_parenthesis

class Environment():
    def __init__(self, variables = {}, parent = None):
        '''initializes an environment'''
        self.variables = variables
        self.parent = parent
    
    def get_var(self, var_name):
        '''finds the value corresponding with a variable name
        this value can also be a function
        if the value can't be found in this environment or in the 
        parent environments, raises a SnekNameError'''
        print(self.variables, 'looking for ', var_name)
        if var_name not in self.variables:
            if self.parent is None:
                raise SnekNameError("Name error - couldn't find variable")
                
            else:
                return self.parent.get_var(var_name)
        else:
            return self.variables[var_name]
    
    def get_parent(self):
        '''returns the parent environment of that environment'''
        return self.parent
    
    def add_var(self, var_name, var_value):
        '''adds a variable and a corresponding value to the environment'''
        self.variables[var_name] = var_value
            
class aFunction():
    def __init__(self, parentEnv, lambda_tree):
        '''initializes a function'''
        self.parentEnv = parentEnv #the parent environment of that function
        
        #the function description with lambda, a parameters list and the function description
        self.lambda_tree = lambda_tree 
    
    def __call__(self, args):
        '''runs when you attempt to call the instance of the class'''
        
        args_list = self.lambda_tree[1]
        function_descrip = self.lambda_tree[2]
        #makes a new environment for that function
        enviro = Environment({}, self.parentEnv)
        
        #if the length of given arguments isn't the same as the number
        #of declared arguments, raise an Evaluation Error
        if len(args) != len(args_list):
            raise SnekEvaluationError("Evaluation error")
        
        #assigns all the parameter names to their corresponding 
        for i in range(len(args)):
            enviro.add_var(args_list[i], args[i])
        

        return evaluate(function_descrip, enviro)
    
    def checkValidFunction(self):
        '''this checks if the function is a valid one (aka if there are no 
        variables being used that haven't been declared in the parameters list
        or previously assigned)'''
    
        args_list = self.lambda_tree[1]
        function_descrip = self.lambda_tree[2]
        #makes a new environment for the function
        envirot = Environment({}, self.parentEnv)
        
        #assigns the parameters list to just any string so that they can be found
        for i in range(len(args_list)):
            envirot.add_var(args_list[i], 'blank')
        
        #check to see if all variables are valid 
        if type(function_descrip) == list:
            for i in function_descrip:
                if i == 'lambda' or i == 'define':
                    break
                if type(i) == str:
                    
                    #doesn't need to store them, just has to make sure that it can be found
                    envirot.get_var(i)
        if type(function_descrip) == str:
            envirot.get_var(function_descrip)
        #deletes the environment and the blank variables later
        del envirot
        return True
        
    
######################
# Built-in Functions #
######################
def mult(args):
    result = 1
    for each in args:
        result = result*each
    return result

def div(args):
    first = args[0]
    for each in args[1:]:
        first = first / each
    return first

def allEqual(args):
    firstArg = args[0]
    for each in args[1:]:
        if firstArg != each:
            return False
    return True

def decreasing(args):
    tempArg = args[0]
    for each in args[1:]:
        if tempArg < each:
            return False
        tempArg = each
    return True

def nonincreasing(args):
    tempArg = args[0]
    for each in args[1:]:
        if tempArg <= each:
            return False
        tempArg = each
    return True

def increasing(args):
    tempArg = args[0]
    for each in args[1:]:
        if tempArg > each:
            return False
        tempArg = each
    return True

def nondecreasing(args):
    tempArg = args[0]
    for each in args[1:]:
        if tempArg >= each:
            return False
        tempArg = each
    return True

snek_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': mult,
    '/': div, 
    '=?': allEqual,
    '>': decreasing,
    '>=': nonincreasing,
    '<': increasing,
    '<=': nondecreasing,
    'not': lambda arg: not arg, 
    '#t': True,
    '#f': False
}

##############
# Evaluation #
##############


def result_and_env(tree, env = None):
    #if its the first time, it makes a first "global" environment
    print(tree)
    
    if env is None:
        built_ins = Environment(snek_builtins)
        env = Environment({}, built_ins)
    
    s = evaluate(tree, env)
    return s, env


def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    #if no environment is given, create a starting environment 
    if env is None:
        built_ins = Environment(snek_builtins)
        env = Environment({}, built_ins)
    print(tree)
    #if it is a number, just return it
    if type(tree) == int or type(tree) == float:
        return tree
    
    elif type(tree) == list:
        #if it is a function with define
        if tree[0] == 'define':
            #if the first element after define is a list, that means its declaring a function
            if type(tree[1]) == list:
                if tree[1] == []:
                    raise SnekSyntaxError('Syntax error')
                
                #convert it to its lambda version
                newTree = ['define', tree[1][0], ['lambda', tree[1][1:], tree[2]]]
              
            else:
                newTree = tree
            #adds a variable that corresponds to the tree[2] value (or function)
            env.add_var(newTree[1], evaluate(newTree[2], env))
            return  evaluate(newTree[2], env)
        
        #if its a lambda, makes a function class instance
        elif tree[0] == 'lambda': 
            return aFunction(env, tree)
        
        elif tree[0] == 'if':
            #checking if right length !!!!! might not be needed here
            if len(tree) != 4:
                return SnekSyntaxError("If statement didn't have the right amount of elements")
         
            elif evaluate(tree[1], env):
                return evaluate(tree[2], env)
            else:
                return evaluate(tree[3], env)
        
        elif tree[0] == 'and':
            for eachElem in tree[1:]:
                if not evaluate(eachElem, env):
                    return False
            return True
        
        elif tree[0] == 'or':
            for eachElem in tree[1:]:
                if evaluate(eachElem, env):
                    return True
            return False
        
        else:
            newlist = []
            #evaluates all the elemtents
            for element in tree:
                newlist.append(evaluate(element, env))
            
            #if its a function class, checks if its a valid function
            if isinstance(newlist[0], aFunction):
                newlist[0].checkValidFunction()
              
            #tries to apply the function on the first element to the other elements
            #on the list
            try:
                return newlist[0](newlist[1:])
            except TypeError:
                raise SnekEvaluationError("Evaluation Error")
    else:
        #if it is just a string, return its corresponding value
        return env.get_var(tree)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    
    inp = input('in> ')
    env = None
    while inp != 'QUIT':
        try:
            res, env = result_and_env(parse(tokenize(inp)), env)
            print('   out>', res)
        except Exception as e:
            print(e)
            print('Error was reached')
        inp = input('in> ')
