# Interpreter-6.009_Project
 Creating a simple interpreter that is able to evaluate arbitrality complicated programs. 
 
 This interpreter is for a dialect of LISP called Snek and it is Turing-complete. All relevant code is in lab.py. To use the interpreter simply run lab.py.
 
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
