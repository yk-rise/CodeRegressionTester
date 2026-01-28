// 版本B：改进的排序算法（快速排序）
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

void quick_sort(int arr[], int low, int high) {
    if (low < high) {
        // 分区操作
        int pivot = arr[high];
        int i = low - 1;
        
        for (int j = low; j <= high - 1; j++) {
            if (arr[j] < pivot) {
                i++;
                // 交换元素
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
        // 交换pivot到正确位置
        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;
        
        int pi = i + 1;
        
        // 递归排序
        quick_sort(arr, low, pi - 1);
        quick_sort(arr, pi + 1, high);
    }
}

int main() {
    int data[1000];
    int count = 0;
    
    // 读取输入数据
    while (scanf("%d", &data[count]) == 1 && count < 1000) {
        count++;
    }
    
    if (count == 0) {
        printf("Error: No input data provided\n");
        return 1;
    }
    
    printf("Input array: ");
    for (int i = 0; i < count; i++) {
        printf("%d ", data[i]);
    }
    printf("\n");
    
    // 排序
    quick_sort(data, 0, count - 1);
    
    printf("Sorted array: ");
    for (int i = 0; i < count; i++) {
        printf("%d ", data[i]);
    }
    printf("\n");
    
    // 统计信息
    printf("Array length: %d\n", count);
    printf("Minimum: %d\n", data[0]);
    printf("Maximum: %d\n", data[count-1]);
    
    // 计算统计信息
    double sum = 0;
    double sum_sq = 0;
    for (int i = 0; i < count; i++) {
        sum += data[i];
        sum_sq += data[i] * data[i];
    }
    double mean = sum / count;
    double variance = (sum_sq / count) - (mean * mean);
    
    printf("Mean: %.4f\n", mean);
    printf("Variance: %.4f\n", variance);
    printf("Standard deviation: %.4f\n", sqrt(variance));
    
    // 额外信息
    printf("Median: %d\n", count % 2 == 1 ? data[count/2] : (data[count/2-1] + data[count/2]) / 2);
    
    return 0;
}