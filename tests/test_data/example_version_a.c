#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// 简单的数学计算函数示例
double calculate_mean(int *data, int size) {
    double sum = 0.0;
    for (int i = 0; i < size; i++) {
        sum += data[i];
    }
    return sum / size;
}

double calculate_variance(int *data, int size, double mean) {
    double sum_sq = 0.0;
    for (int i = 0; i < size; i++) {
        sum_sq += (data[i] - mean) * (data[i] - mean);
    }
    return sum_sq / size;
}

int main() {
    int data[100];
    int size = 0;
    
    // 从标准输入读取数据
    while (scanf("%d", &data[size]) == 1 && size < 100) {
        size++;
    }
    
    if (size == 0) {
        printf("Error: No data input\n");
        return 1;
    }
    
    // 计算统计量
    double mean = calculate_mean(data, size);
    double variance = calculate_variance(data, size, mean);
    double std_dev = sqrt(variance);
    
    // 输出结果
    printf("Sample size: %d\n", size);
    printf("Mean: %.6f\n", mean);
    printf("Variance: %.6f\n", variance);
    printf("Standard deviation: %.6f\n", std_dev);
    
    // 找出最小值和最大值
    int min = data[0], max = data[0];
    for (int i = 1; i < size; i++) {
        if (data[i] < min) min = data[i];
        if (data[i] > max) max = data[i];
    }
    
    printf("Min: %d\n", min);
    printf("Max: %d\n", max);
    printf("Range: %d\n", max - min);
    
    return 0;
}