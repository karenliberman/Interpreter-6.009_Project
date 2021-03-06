# Interpreter-6.009_Project
 Creating a simple interpreter that is able to evaluate arbitrality complicated programs. 
 
 This interpreter is for a dialect of LISP called Snek and it is Turing-complete. All relevant code is in lab.py. To use the interpreter simply run lab.py. By running the file you will be using the REPL, which will continually prompt for input until you type QUIT. 
 
# Example Programs to run 
** NOTE - the REPL does not accept multiple lines code
### Absolute Value Program
Takes a number n as input and returns |n|.

    (define (abs n)
     (if (< n 0) (* n -1) n)
    )
### Factorial Program
Takes a nonnegative integer n as input and returns n!.

    (define (factorial n)

    (if (=? n 0) 1 (* n (factorial (- n 1))))
    )

### Polynomial Evaluation
We'll represent polynomials in xx as lists of coefficients, starting with the zeroth-order coefficient. For example, we would represent x^2 as (list 0 0 1), and 4x^3 + 7x - 8 as (list -8 7 0 4).
Your function should take two arguments: a list containing coefficients in this form and a value to plug in for xx; and it should return a single number representing the value of the polynomial at that value of xx. 

    (define (poly-val coeffs x)

    (if (=? coeffs nil) 0 
    (+ (car coeffs) (* x (poly-val(cdr coeffs) x))))

    )

### Range
It is a function that replicates the behavior of range in Python. It has the format (range start stop step) and outputs a list containing the same numbers that would exist in Python's range(start, stop, step).
Unlike Python's range, it handles the cases of positive step arguments, and all three arguments must be provided.

    (define (range start stop step)
    (if (< start stop) (concat (list start) (range (+ start step) stop step) ) nil)
    )

# Coding in the Interpreter (with examples)
 
All-in-all, we can define the syntax of Snek as follows:

- Numbers (e.g., 1) and symbols (things like variable names, e.g., x) are called atomic expressions; they cannot be broken into pieces. These are similar to their Python counterparts, except that in Snek, operators such as + and > are symbols, too, and are treated the same way as x and fib.
- Everything else is an S-expression: an opening round bracket (, followed by one or more expressions, followed by a closing round bracket ). The first subexpression determines what the S-expression means:
   - An S-expression starting with a keyword, e.g. (define ...), is a special form; the meaning depends on the keyword.
   - An S-expression starting with a non-keyword, e.g. (fn ...), is a function call, where the first element in the expression is the function to be called, and the remaining subexpressions represent the arguments to that function.
For example, consider the following definition of a function that computes Fibonacci numbers in Python:

    def fib(n):
        if n <= 1:
            return n
        return fib(n-1) + fib(n-2)
    
We could write an equivalent program in Snek:

    (define fib
      (lambda (n)
        (if (<= n 1)
          n
          (+ (fib (- n 1)) (fib (- n 2)))
        )
      )
    )
More examples - 

    > (+ 3 2)

      => 5


    > (define (square x) (* x x))

      => FUNCTION: (lambda (x) (* x x))


    > (define (fourthpower x) (square (square x)))

      => FUNCTION: (lambda (x) (square (square x)))


    > (fourthpower 1.1)

      => 1.4641000000000004


    > (+ 3 (- 7 8))

      => 2

You can also use the operations *, /, 

### Defining variables
A variable definition has the following syntax: (define NAME EXPR), where NAME is a symbol and EXPR is an arbitrary expression.

    in> (define pi 3.14)
      out> 3.14

    in> (define radius 2)
      out> 2

    in> (* pi radius radius)
      out> 12.56

    in> QUIT
    
### Defining functions
A lambda expression takes the following form: (lambda (PARAM1 PARAM2 ...) EXPR). The result of evaluating such an expression should be an object representing that function (note that this expression represents a function definition, not a function call). Note that variables are stored in different environments and that functions have their own environments. Example: 

    in> (define square (lambda (x) (* x x)))
        out> function object

    in> (square 2)
        out> 4
    in> ((lambda (x) (* x x)) 3)
        out> 9
        
Or, you can define functions such as that
  - (define (five) (+ 2 3)) should be equivalent to (define five (lambda () (+ 2 3)))
  - (define (square x) (* x x)) should be equivalent to (define square (lambda (x) (* x x)))
  - (define (add2 x y) (+ x y)) should be equivalent to (define add2 (lambda (x y) (+ x y)))
  
### Conditionals
Have the following form: (if COND TRUEEXP FALSEEXP). If COND evaluates to true, the result of this expression is the result of evaluating TRUEEXP; if COND instead evaluates to false, the result of this expression is the result of evaluating FALSEEXP.

  -  =? should evaluate to true if all of its arguments are equal to each other.
  -  > should evaluate to true if its arguments are in decreasing order.
  -  >= should evaluate to true if its arguments are in nonincreasing order.
  -  < should evaluate to true if its arguments are in increasing order.
  -  <= should evaluate to true if its arguments are in nondecreasing order.

### Lists
Are implemented as Linked Lists. nil represents None. Calling (cons 1 2) should result in a new Pair object whose car is 1 and whose cdr is 2.
  - (list) should evaluate to the same thing as nil
  - (list 1) should evaluate to the same thing as (cons 1 nil)
  - (list 1 2) should evaluate to the same thing as (cons 1 (cons 2 nil))

OPERATING ON LISTS (METHODS)
  -  (length LIST) should take a list as argument and should return the length of that list. When called on any object that is not a linked list, it should raise a SnekEvaluationError.
  -  (elt-at-index LIST INDEX) should take a list and a nonnegative index, and it should return the element at the given index in the given list. As in Python, indices start from 0. If LIST is a cons cell (but not a list), then asking for index 0 should produce the car of that cons cell, and asking for any other index should raise a SnekEvaluationError. You do not need to support negative indices.
  -  (concat LIST1 LIST2 LIST3 ...) should take an arbitrary number of lists as arguments and should return a new list representing the concatenation of these lists. If exactly one list is passed in, it should return a copy of that list. If concat is called with no arguments, it should produce an empty list. Calling concat on any elements that are not lists should result in a SnekEvaluationError.
  
  -  (map FUNCTION LIST) takes a function and a list as arguments, and it returns a new list containing the results of applying the given function to each element of the given list.
     For example, (map (lambda (x) (* 2 x)) (list 1 2 3)) should produce the list (2 4 6).

  -  (filter FUNCTION LIST) takes a function and a list as arguments, and it returns a new list containing only the elements of the given list for which the given function returns true.
     For example, (filter (lambda (x) (> x 0)) (list -1 2 -3 4)) should produce the list (2 4).

  -  (reduce FUNCTION LIST INITVAL) takes a function, a list, and an initial value as inputs. It produces its output by successively applying the given function to the elements in the list, maintaining an intermediate result along the way. This is perhaps the most difficult of the three functions to understand, but it may be easiest to see by example.
     Consider (reduce * (list 9 8 7) 1). The function in question is *. Our initial value is 1. We take this value and combine it with the first element in the list using the given function, giving us (* 1 9) or 9. Then we take this result and combine it with the next element in the list using the given function, giving us (* 9 8) or 72. Then we take this result and combine it with the next element in the list using the given function, giving us (* 72 7) or 504. Since we have reached the end of the list, this is our final return value (if there were more elements in the list, we would keep combining our "result so far" with the next element in the list, using the given function).
     
     
 ### Let
let is used for creating local variable definitions. It takes the form: (let ((VAR1 VAL1) (VAR2 VAL2) (VAR3 VAL3) ...) BODY), where VAR1, VAR2, etc., are variable names, and VAL1, VAL2, etc., are expressions denoting the values to which those names should be bound. It works by:
  - Evaluating all the given values in the current environment.
  - Creating a new environment whose parent is the current environment, binding each name to its associated value in this new environment.
  - Evaluating the BODY expression in this new environment (this value is the result of evaluating the let special form).
Note that the given bindings are only available in the body of the let expression. For example:

    in> (define z 5)
        out> 5

    in> (let ((x 5) (y 3)) (+ x y z))
        out> 13

    in> x
        EXCEPTION!

    in> y
        EXCEPTION!

    in> z
        out> 5
         

### Set
set! (often pronounced "set-bang") is used for changing the value of an existing variable. It takes the form: (set! VAR EXPR), where VAR is a variable name, and EXPR is an expression.
It should work by:
  - Evaluating the given expression in the current environment
  - Finding the nearest enclosing environment in which VAR is defined (starting from the current environment and working upward until it finds a binding), and updating its binding in that environment to be the result of evaluating EXPR
It should also evaluate to that same value.

If VAR is not defined in any environments in the chain, set! should raise a SnekNameError.

    in> (define x 7)
        out> 7

    in> (define (foo z) (set! x (+ z 2)))
        out> function object

    in> (foo 3)
        out> 5

    in> x
        out> 5

    in> (define (bar z) (define x (+ z 2)))
        out> function object

    in> (bar 7)
        out> 9

    in> x
        out> 5
