#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// 改进的数学计算函数示例（版本B）
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
    return sum_sq / (size - 1);  // 使用样本方差（分母为n-1）
}

// 新增：计算中位数
double calculate_median(int *data, int size) {
    // 简单的排序
    for (int i = 0; i < size - 1; i++) {
        for (int j = i + 1; j < size; j++) {
            if (data[i] > data[j]) {
                int temp = data[i];
                data[i] = data[j];
                data[j] = temp;
            }
        }
    }
    
    if (size % 2 == 0) {
        return (data[size/2 - 1] + data[size/2]) / 2.0;
    } else {
        return data[size/2];
    }
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
    
    // 创建副本用于中位数计算
    int *data_copy = malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
        data_copy[i] = data[i];
    }
    
    // 计算统计量
    double mean = calculate_mean(data, size);
    double variance = calculate_variance(data, size, mean);
    double std_dev = sqrt(variance);
    double median = calculate_median(data_copy, size);
    
    // 输出结果（格式略有不同）
    printf("Data Analysis Results:\n");
    printf("====================\n");
    printf("Sample size: %d\n", size);
    printf("Mean: %.8f\n", mean);        // 更高精度
    printf("Median: %.8f\n", median);    // 新增中位数
    printf("Variance (sample): %.8f\n", variance);
    printf("Standard deviation: %.8f\n", std_dev);
    
    // 找出最小值和最大值
    int min = data[0], max = data[0];
    for (int i = 1; i < size; i++) {
        if (data[i] < min) min = data[i];
        if (data[i] > max) max = data[i];
    }
    
    printf("Min: %d\n", min);
    printf("Max: %d\n", max);
    printf("Range: %d\n", max - min);
    
    // 新增：输出四分位数
    printf("Q1: %.8f\n", calculate_median(data_copy, size/4));
    printf("Q3: %.8f\n", calculate_median(data_copy + (3*size)/4, size/4));
    
    free(data_copy);
    return 0;
}