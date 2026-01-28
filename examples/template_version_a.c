/*
 * 版本A：简单的平方函数
 */
#include <stdio.h>
#include <stdlib.h>

// 要测试的函数
int square(int x) {
    return x * x;
}

int cube(int x) {
    return x * x * x;
}

int max_of_two(int a, int b) {
    return (a > b) ? a : b;
}

int main() {
    int data[100];
    int count = 0;
    
    // 读取数组数据
    while (scanf("%d", &data[count]) == 1 && count < 100) {
        count++;
    }
    
    if (count == 0) {
        printf("Error: No input data\n");
        return 1;
    }
    
    printf("Input array: ");
    for (int i = 0; i < count; i++) {
        printf("%d ", data[i]);
    }
    printf("\n\n");
    
    // 处理每个元素
    printf("Processing results:\n");
    for (int i = 0; i < count; i++) {
        int val = data[i];
        printf("Value %d: square=%d, cube=%d\n", 
               val, square(val), cube(val));
    }
    
    // 找最大值
    if (count >= 2) {
        int max_val = max_of_two(data[0], data[1]);
        for (int i = 2; i < count; i++) {
            max_val = max_of_two(max_val, data[i]);
        }
        printf("Maximum value: %d\n", max_val);
    }
    
    return 0;
}