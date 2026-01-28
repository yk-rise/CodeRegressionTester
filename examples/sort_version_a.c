// 版本A：简单的排序算法（冒泡排序）
#include <stdio.h>
#include <stdlib.h>

void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                // 交换元素
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
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
        printf("Error: No input data\n");
        return 1;
    }
    
    printf("Original array: ");
    for (int i = 0; i < count; i++) {
        printf("%d ", data[i]);
    }
    printf("\n");
    
    // 排序
    bubble_sort(data, count);
    
    printf("Sorted array: ");
    for (int i = 0; i < count; i++) {
        printf("%d ", data[i]);
    }
    printf("\n");
    
    // 统计信息
    printf("Array size: %d\n", count);
    printf("Min element: %d\n", data[0]);
    printf("Max element: %d\n", data[count-1]);
    
    // 计算平均值
    double sum = 0;
    for (int i = 0; i < count; i++) {
        sum += data[i];
    }
    printf("Average: %.2f\n", sum / count);
    
    return 0;
}