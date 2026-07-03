(+ 2 3)
(car '(1 2 3))
(define f (lambda (x) (+ x 1)))
(f 2)
(define factorial
  (lambda (n)
    (cond
      ((<= n 1) 1)
      (else (* n (factorial (- n 1)))))))
(factorial 5)
