// 版本B：改进的数学计算
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// 递归计算阶乘（带缓存）
long factorial_cached(int n, long cache[]) {
    if (n < 0) return -1;
    if (n == 0 || n == 1) return 1;
    if (cache[n] != 0) return cache[n];
    
    cache[n] = n * factorial_cached(n - 1, cache);
    return cache[n];
}

long factorial(int n) {
    if (n > 20) return -1; // 防止溢出
    
    long cache[21] = {0};
    return factorial_cached(n, cache);
}

// 动态规划计算斐波那契
int fibonacci_dp(int n) {
    if (n < 0) return -1;
    if (n == 0) return 0;
    if (n == 1) return 1;
    
    int *fib = malloc((n + 1) * sizeof(int));
    fib[0] = 0;
    fib[1] = 1;
    
    for (int i = 2; i <= n; i++) {
        fib[i] = fib[i - 1] + fib[i - 2];
    }
    
    int result = fib[n];
    free(fib);
    return result;
}

// 新增：计算最大公约数
int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// 新增：计算最小公倍数
int lcm(int a, int b) {
    if (a == 0 || b == 0) return 0;
    return abs(a * b) / gcd(a, b);
}

int main() {
    int n1, n2;
    
    if (scanf("%d %d", &n1, &n2) != 2) {
        printf("Error: Invalid input format. Expected: <num1> <num2>\n");
        return 1;
    }
    
    printf("Mathematical Analysis Report:\n");
    printf("=============================\n");
    printf("Input values: %d and %d\n\n", n1, n2);
    
    // 阶乘计算
    long fact1 = factorial(n1);
    long fact2 = factorial(n2);
    
    printf("Factorial Results:\n");
    if (fact1 >= 0) {
        printf("  %d! = %ld\n", n1, fact1);
    } else {
        printf("  %d! = Error (negative or too large)\n", n1);
    }
    
    if (fact2 >= 0) {
        printf("  %d! = %ld\n", n2, fact2);
    } else {
        printf("  %d! = Error (negative or too large)\n", n2);
    }
    
    if (fact1 > 0 && fact2 > 0) {
        double ratio = (double)fact1 / fact2;
        printf("  Ratio (%d!/%d!) = %.6f\n", n1, n2, ratio);
    }
    
    // 斐波那契计算
    int fib1 = fibonacci_dp(n1);
    int fib2 = fibonacci_dp(n2);
    
    printf("\nFibonacci Results:\n");
    printf("  F(%d) = %d\n", n1, fib1);
    printf("  F(%d) = %d\n", n2, fib2);
    printf("  F(%d) + F(%d) = %d\n", n1, n2, fib1 + fib2);
    
    // 新增计算
    printf("\nAdditional Calculations:\n");
    
    if (n1 >= 0 && n2 >= 0) {
        printf("  GCD(%d, %d) = %d\n", n1, n2, gcd(abs(n1), abs(n2)));
        printf("  LCM(%d, %d) = %d\n", n1, n2, lcm(n1, n2));
        
        if (n1 != 0 && n2 != 0) {
            printf("  Product: %d\n", n1 * n2);
            printf("  Quotient: %.4f\n", (double)n1 / n2);
        }
    }
    
    // 数论性质
    printf("\nNumber Theory Properties:\n");
    printf("  %d is %s\n", n1, n1 % 2 == 0 ? "even" : "odd");
    printf("  %d is %s\n", n2, n2 % 2 == 0 ? "even" : "odd");
    
    // 判断素数（简单方法）
    int is_prime1 = (n1 > 1) ? 1 : 0;
    int is_prime2 = (n2 > 1) ? 1 : 0;
    
    for (int i = 2; i * i <= n1 && is_prime1; i++) {
        if (n1 % i == 0) is_prime1 = 0;
    }
    
    for (int i = 2; i * i <= n2 && is_prime2; i++) {
        if (n2 % i == 0) is_prime2 = 0;
    }
    
    printf("  %d is %s\n", n1, is_prime1 ? "prime" : "composite");
    printf("  %d is %s\n", n2, is_prime2 ? "prime" : "composite");
    
    return 0;
}