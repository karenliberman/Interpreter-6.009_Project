# Interpreter-6.009_Project
 Creating a simple interpreter that is able to evaluate arbitrality complicated programs. 
 
 This interpreter is for a dialect of LISP called Snek and it is Turing-complete. All relevant code is in lab.py. To use the interpreter simply run lab.py. By running the file you will be using the REPL, which will continually prompt for input until you type QUIT. 
 
# Example Programs to run 

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
