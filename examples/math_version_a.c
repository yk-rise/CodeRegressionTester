// 版本A：基础数学计算
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// 计算阶乘
long factorial(int n) {
    if (n < 0) return -1;
    if (n == 0 || n == 1) return 1;
    
    long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

// 计算斐波那契数列
int fibonacci(int n) {
    if (n < 0) return -1;
    if (n == 0) return 0;
    if (n == 1) return 1;
    
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int main() {
    int n1, n2;
    
    if (scanf("%d %d", &n1, &n2) != 2) {
        printf("Error: Invalid input format\n");
        return 1;
    }
    
    printf("Input numbers: %d, %d\n", n1, n2);
    
    // 计算阶乘
    long fact1 = factorial(n1);
    long fact2 = factorial(n2);
    
    if (fact1 >= 0 && fact2 >= 0) {
        printf("Factorial of %d: %ld\n", n1, fact1);
        printf("Factorial of %d: %ld\n", n2, fact2);
        printf("Ratio: %.4f\n", (double)fact1 / fact2);
    } else {
        printf("Error: Negative input for factorial\n");
    }
    
    // 计算斐波那契
    int fib1 = fibonacci(n1);
    int fib2 = fibonacci(n2);
    
    if (fib1 >= 0 && fib2 >= 0) {
        printf("Fibonacci of %d: %d\n", n1, fib1);
        printf("Fibonacci of %d: %d\n", n2, fib2);
        printf("Sum: %d\n", fib1 + fib2);
    }
    
    return 0;
}