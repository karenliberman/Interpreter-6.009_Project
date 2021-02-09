#!/usr/bin/env python3
"""6.009 Lab 9: Snek Interpreter"""

import doctest
import sys
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

        if var_name not in self.variables:
            if self.parent is None:
                raise SnekNameError("Name error - couldn't find variable")
                
            else:
                return self.parent.get_var(var_name)
        else:
            return self.variables[var_name]
    
    def set_var(self, var_name, var_value):
        '''sets the variable into the given value once the corresponding
        variable name is found
        if the value can't be found in this environment or in the 
        parent environments, raises a SnekNameError'''
        if var_name not in self.variables:
            if self.parent is None:
                raise SnekNameError("Name error - couldn't find variable")
                
            else:
                return self.parent.set_var(var_name, var_value)
        else:
            self.variables[var_name] = var_value
            return var_value
        
        
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
                if i == 'lambda' or i == 'define' or i == 'set!':
                    break
                if type(i) == str:
                    
                    #doesn't need to store them, just has to make sure that it can be found
                    envirot.get_var(i)
        if type(function_descrip) == str:
            envirot.get_var(function_descrip)
        #deletes the environment and the blank variables later
        del envirot
        return True

class Pair():
    def __init__(self, car, cdr):
        '''initializes a pair that can be used to form a linked list'''
        self.car = car
        self.cdr = cdr
    
    
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
        if tempArg <= each:
            return False
        tempArg = each
    return True

def nonincreasing(args):
    tempArg = args[0]
    for each in args[1:]:
        if tempArg < each:
            return False
        tempArg = each
    return True

def increasing(args):
    tempArg = args[0]
    for each in args[1:]:
        if tempArg >= each:
            return False
        tempArg = each
    return True

def nondecreasing(args):
    tempArg = args[0]
    for each in args[1:]:
        if tempArg > each:
            return False
        tempArg = each
    return True

def makingList(args): 
    
    if args == []:
        return None #maybe switch to nil?
    else:
        return snek_builtins['cons']([args[0], makingList(args[1:])])

def car(x):
    if isinstance(x[0], Pair):
        return x[0].car
    else: 
        raise SnekEvaluationError

def cdr(x):
    if isinstance(x[0], Pair):
        return x[0].cdr
    else: 
        raise SnekEvaluationError

def length(arg):
    '''returns the length of a list'''
    if arg[0] is None:
        return 0
    #check if a list
    elif isinstance(arg[0], Pair) and (isinstance(arg[0].cdr, Pair) or arg[0].cdr is None):
        count = 1
        cdrVal = arg[0]
        
        while cdrVal.cdr is not None:
           count += 1 
           cdrVal = cdrVal.cdr
           
        return count 
    else:
        raise SnekEvaluationError("Tried to take a length of something other than a list")

def atIndex(arg):
    '''returns the element at a given index of a list'''
    try:
        theList = arg[0]
        index = arg[1]
        car = theList.car

        while index != 0:
            index -= 1
            theList = theList.cdr
            car = theList.car

        return car
    except: 
        raise SnekEvaluationError("Issue at atIndex!")

def concat(args, initialVal = None, finalLink = None):
    '''concatenates any number of lists'''
    if args == []:
        return []

    currentPair = args[0]
    
    #if current pair is not a list, skip it (if there are values after)
    if (currentPair == [] or currentPair is None) and len(args) > 1:
        return concat(args[1:], initialVal, finalLink)
    #if current pair is not a list and there are no values after, return initialVal
    elif (currentPair == [] or currentPair is None) and len(args) == 1:
        return initialVal
    
    #if something other than a pair was inputed into concat, raise an error
    if not isinstance(currentPair, Pair) or (currentPair.cdr != None and not isinstance(currentPair.cdr, Pair)):
        raise SnekEvaluationError("Inputed something other than a pair in Concat")
    
    #means this is the first list being added
    if initialVal is None:
        initialVal = Pair(currentPair.car, None)
        finalLink = initialVal
    else: 
        finalLink.cdr = Pair(currentPair.car, None)
        finalLink = finalLink.cdr
    
    while currentPair.cdr is not None:
            currentPair = currentPair.cdr
            finalLink.cdr = Pair(currentPair.car, None) 
            finalLink = finalLink.cdr
    
    #base case
    if len(args) == 1:
        return initialVal
    else:
        return concat(args[1:], initialVal, finalLink)

def mapping(args_list):
    '''applies a givn functin to all the elements of a given list and returns the new list'''
    function = args_list[0]
    initialLink = args_list[1]
    if initialLink is None or initialLink == []:
        return None
    #checks if the list is an actual list
    if not isinstance(initialLink, Pair):
        raise SnekEvaluationError("Non pair list in Map")

    newInitialLink = Pair(function([initialLink.car]), None)
    newFinalLink = newInitialLink

    while initialLink.cdr is not None:
        initialLink = initialLink.cdr
        newFinalLink.cdr = Pair(function([initialLink.car]), None)

        newFinalLink = newFinalLink.cdr
    
    return newInitialLink
    
def filterFunc(args_list):
    '''checks all the elements of a list and returns a new list with only the 
    elements for which the given function returned true'''
    
    function = args_list[0]
    initialLink = args_list[1]
    
    if initialLink is None or initialLink == []:
        return None
    #checks if a valid list
    if not isinstance(initialLink, Pair):
        raise SnekEvaluationError("Non pair list in filter")
    
    initialFinalLink = None
    firstTime = True
    
    while initialLink is not None:
        if function([initialLink.car]):
            if firstTime:
                currentLink = Pair(initialLink.car, None)
                initialFinalLink = currentLink
                firstTime = False
            else: 
                currentLink.cdr = Pair(initialLink.car, None)
                currentLink = currentLink.cdr

        initialLink = initialLink.cdr
        
    return initialFinalLink

def reduce(args_list):
    '''takes a function, a list and an initial value as ipus
    it applies the function to an initial value and the list item, but
    it goes maintaining an intermediate result along the way'''
    function = args_list[0]
    originalLink = args_list[1]
    initVal = args_list[2]
    
    if originalLink is None or originalLink == []:
        return initVal

    if not isinstance(originalLink, Pair):
        raise SnekEvaluationError("Non pair list in reduce")
        
    initVal = function([initVal, originalLink.car])
    #goes passing thorugh each list element and saving the new intermediate value
    while originalLink.cdr is not None:
        originalLink = originalLink.cdr
        initVal = function([initVal, originalLink.car])
    
    return initVal
    
def evaluate_file(fileName, env = None): 
    '''evaluates a file and adds it to our current or a global environment'''
    if env is None:
        built_ins = Environment(snek_builtins)
        env = Environment({}, built_ins)
        
    finalString = '(begin '
        
    with open(fileName, 'r') as f:
        for i in f:
            finalString = finalString + i
    
    return evaluate(parse(tokenize(finalString + ")")), env)
        
    
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
    'not': lambda arg: not arg[0], 
    'if': None,
    '#t': True,
    '#f': False, 
    'cons': lambda args: Pair(args[0], args[1]),
    'car': car,
    'cdr': cdr,
    'nil': None,
    'list': makingList,
    'length': length, 
    'elt-at-index': atIndex,
    'concat': concat,
    'map': mapping, 
    'filter': filterFunc, 
    'reduce': reduce,
    'begin': lambda args: args[len(args)-1]
    
}

##############
# Evaluation #
##############(if (< start stop) (concat (range  start (- stop step) step) (list (- stop step))) nil)


def result_and_env(tree, env = None):
    #if its the first time, it makes a first "global" environment
    
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
    #if it is a number, just return it
    if type(tree) == int or type(tree) == float:
        return tree
    
    elif type(tree) == list:
        #if it is a function with define
        if tree == []:
            raise SnekEvaluationError('Empty list for a tree')
        elif tree[0] == 'define':
            #if the first element after define is a list, that means its declaring a function
            if type(tree[1]) == list:
                if tree[1] == []:
                    raise SnekSyntaxError('Syntax error')
                
                #convert it to its lambda version
                newTree = ['define', tree[1][0], ['lambda', tree[1][1:], tree[2]]]
              
            else:
                newTree = tree
            #adds a variable that corresponds to the tree[2] value (or function)
            newVal = evaluate(newTree[2], env)
            env.add_var(newTree[1], newVal)
            return newVal
        
        #if its a lambda, makes a function class instance
        elif tree[0] == 'lambda': 
            return aFunction(env, tree)
        
        #takes care of the special for 'if'
        elif tree[0] == 'if':
            #checking if right length
            if len(tree) != 4:
                return SnekSyntaxError("If statement didn't have the right amount of elements")

            if evaluate(tree[1], env):
                return evaluate(tree[2], env)
            else:
                return evaluate(tree[3], env)
        
        #takes cares of the special form 'and'
        elif tree[0] == 'and':
            for eachElem in tree[1:]:
                if not evaluate(eachElem, env):
                    return False
            return True
        
        #takes care of the special form 'or'
        elif tree[0] == 'or':
            for eachElem in tree[1:]:
                if evaluate(eachElem, env):
                    return True
            return False
        
        #takes care of the special form 'let'
        elif tree[0] == 'let':
            variables = tree[1]
            body = tree[2]
            variablesDict  = {}
            for eachVar in variables:
                variablesDict[eachVar[0]] = evaluate(eachVar[1], env)
            
            #makes a new environment with the new assigned variables, its parent
            #environment being the current environment
            newEnv = Environment(variablesDict, env)
            return evaluate(body, newEnv)
        
        #takes care of the special form set
        elif tree[0] == 'set!':
            
            varName = tree[1]
            varValue = evaluate(tree[2], env)
            
            return env.set_var(varName, varValue)
        
        
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
        print('finding ', tree)
        return env.get_var(tree)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    built_ins = Environment(snek_builtins)
    env = Environment({}, built_ins)
    y = sys.argv
    rest = y[1:]
    for i in rest:
        evaluate_file(i, env)
    
    inp = input('in> ')

    while inp != 'QUIT':
        try:
            res, env = result_and_env(parse(tokenize(inp)), env)
            print('   out>', res)
        except Exception as e:
            print(e)
            print('Error was reached')
        inp = input('in> ')
