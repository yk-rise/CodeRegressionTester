/*
 * 版本B：增强的数学函数
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// 要测试的函数（增强版本）
long square_long(int x) {
    return (long)x * x;
}

long cube_long(int x) {
    return (long)x * x * x;
}

int max_of_three(int a, int b, int c) {
    return (a > b) ? (a > c ? a : c) : (b > c ? b : c);
}

// 新增：检查是否为完全平方数
int is_perfect_square(int x) {
    if (x < 0) return 0;
    int root = (int)sqrt(x);
    return root * root == x;
}

// 新增：计算绝对值
int abs_val(int x) {
    return (x < 0) ? -x : x;
}

int main() {
    int data[100];
    int count = 0;
    
    // 读取数组数据
    while (scanf("%d", &data[count]) == 1 && count < 100) {
        count++;
    }
    
    if (count == 0) {
        printf("Error: No input data provided\n");
        return 1;
    }
    
    printf("Mathematical Analysis Report:\n");
    printf("============================\n");
    printf("Input array: ");
    for (int i = 0; i < count; i++) {
        printf("%d ", data[i]);
    }
    printf("\n\n");
    
    // 增强的处理结果
    printf("Enhanced Processing Results:\n");
    for (int i = 0; i < count; i++) {
        int val = data[i];
        long sq = square_long(val);
        long cb = cube_long(val);
        
        printf("Value %d:\n", val);
        printf("  Square: %ld\n", sq);
        printf("  Cube: %ld\n", cb);
        printf("  Is perfect square: %s\n", is_perfect_square(sq) ? "Yes" : "No");
        printf("  Absolute value: %d\n", abs_val(val));
        printf("  Cube root: %.4f\n", cbrt(cb));
        printf("\n");
    }
    
    // 扩展统计
    if (count >= 3) {
        printf("Extended Statistics:\n");
        
        // 计算总和
        long total_sum = 0;
        long square_sum = 0;
        int positive_count = 0, negative_count = 0;
        
        for (int i = 0; i < count; i++) {
            int val = data[i];
            total_sum += val;
            square_sum += square_long(val);
            if (val > 0) positive_count++;
            else if (val < 0) negative_count++;
        }
        
        printf("  Sum of values: %ld\n", total_sum);
        printf("  Sum of squares: %ld\n", square_sum);
        printf("  Positive numbers: %d\n", positive_count);
        printf("  Negative numbers: %d\n", negative_count);
        printf("  Zero numbers: %d\n", count - positive_count - negative_count);
        
        // 找三个最大值
        if (count >= 3) {
            int max1, max2, max3;
            max1 = max2 = max3 = data[0];
            
            for (int i = 1; i < count; i++) {
                if (data[i] > max1) {
                    max3 = max2;
                    max2 = max1;
                    max1 = data[i];
                } else if (data[i] > max2) {
                    max3 = max2;
                    max2 = data[i];
                } else if (data[i] > max3) {
                    max3 = data[i];
                }
            }
            
            printf("  Top 3 maximums: %d, %d, %d\n", max1, max2, max3);
            printf("  Maximum of top 3: %d\n", max_of_three(max1, max2, max3));
        }
        
        // 新增：计算标准差
        double mean = (double)total_sum / count;
        double variance = 0;
        for (int i = 0; i < count; i++) {
            variance += (data[i] - mean) * (data[i] - mean);
        }
        variance /= count;
        double stddev = sqrt(variance);
        
        printf("  Mean: %.4f\n", mean);
        printf("  Variance: %.4f\n", variance);
        printf("  Standard deviation: %.4f\n", stddev);
        printf("  Coefficient of variation: %.4f\n", stddev / mean);
    }
    
    // 新增：检查数字属性
    printf("\nNumber Properties:\n");
    int even_count = 0, odd_count = 0;
    int prime_count = 0;
    
    for (int i = 0; i < count; i++) {
        int val = abs_val(data[i]);
        
        if (val % 2 == 0) even_count++;
        else odd_count++;
        
        // 简单素数检查
        if (val > 1) {
            int is_prime = 1;
            for (int j = 2; j * j <= val; j++) {
                if (val % j == 0) {
                    is_prime = 0;
                    break;
                }
            }
            if (is_prime) prime_count++;
        }
    }
    
    printf("  Even numbers: %d\n", even_count);
    printf("  Odd numbers: %d\n", odd_count);
    printf("  Prime numbers: %d\n", prime_count);
    printf("  Even ratio: %.2f%%\n", (double)even_count / count * 100);
    printf("  Prime ratio: %.2f%%\n", (double)prime_count / count * 100);
    
    return 0;
}