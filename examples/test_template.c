/*
 * 代码回灌测试模板
 * 
 * 使用说明：
 * 1. 在下方 "要测试的函数定义" 区域添加你的函数
 * 2. 在 main() 函数中设置输入参数
 * 3. 编译并运行测试
 * 
 * 支持的测试类型：
 * - 单参数函数
 * - 双参数函数  
 * - 数组处理函数
 * - 自定义输入处理
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// ================================
// 要测试的函数定义区域
// ================================

// 示例1：单参数函数
// int my_function(int param) {
//     return param * 2;
// }

// 示例2：双参数函数
// int my_calculation(int a, int b) {
//     return a + b * 2;
// }

// 示例3：数组处理函数
// void process_array(int arr[], int size) {
//     for (int i = 0; i < size; i++) {
//         arr[i] = arr[i] * 2;
//     }
// }

// 示例4：字符串处理函数
// void process_string(char str[]) {
//     int len = strlen(str);
//     for (int i = 0; i < len; i++) {
//         if (str[i] >= 'a' && str[i] <= 'z') {
//             str[i] = str[i] - 'a' + 'A';
//         }
//     }
// }

// ================================
// 辅助函数
// ================================

// 打印数组
void print_array(int arr[], int size) {
    printf("[");
    for (int i = 0; i < size; i++) {
        printf("%d", arr[i]);
        if (i < size - 1) printf(", ");
    }
    printf("]");
}

// 打印数组统计信息
void print_array_stats(int arr[], int size) {
    if (size == 0) {
        printf("Empty array\n");
        return;
    }
    
    int sum = 0, min = arr[0], max = arr[0];
    for (int i = 0; i < size; i++) {
        sum += arr[i];
        if (arr[i] < min) min = arr[i];
        if (arr[i] > max) max = arr[i];
    }
    
    double mean = (double)sum / size;
    
    printf("Array Statistics:\n");
    printf("  Size: %d\n", size);
    printf("  Sum: %d\n", sum);
    printf("  Mean: %.2f\n", mean);
    printf("  Min: %d\n", min);
    printf("  Max: %d\n", max);
    printf("  Range: %d\n", max - min);
}

// 计算标准差
double calculate_stddev(int arr[], int size, double mean) {
    double sum_sq = 0;
    for (int i = 0; i < size; i++) {
        sum_sq += (arr[i] - mean) * (arr[i] - mean);
    }
    return sqrt(sum_sq / size);
}

// ================================
// 主测试函数
// ================================

// 测试类型枚举
typedef enum {
    TEST_SINGLE_PARAM,    // 单参数函数
    TEST_DOUBLE_PARAM,    // 双参数函数
    TEST_ARRAY_INPUT,     // 数组输入函数
    TEST_CUSTOM           // 自定义测试
} test_type_t;

// 单参数测试
void test_single_param(int param) {
    printf("=== 单参数函数测试 ===\n");
    printf("输入参数: %d\n", param);
    
    // 调用你的函数
    // int result = my_function(param);
    int result = param * 2; // 示例结果
    
    printf("输出结果: %d\n", result);
    printf("结果类型: %s\n", (result % 2 == 0) ? "偶数" : "奇数");
}

// 双参数测试
void test_double_param(int param1, int param2) {
    printf("=== 双参数函数测试 ===\n");
    printf("输入参数1: %d\n", param1);
    printf("输入参数2: %d\n", param2);
    
    // 调用你的函数
    // int result = my_calculation(param1, param2);
    int result = param1 + param2 * 2; // 示例结果
    
    printf("输出结果: %d\n", result);
    printf("参数和: %d\n", param1 + param2);
    printf("参数积: %d\n", param1 * param2);
    printf("参数差: %d\n", abs(param1 - param2));
    printf("参数比: %.3f\n", (double)param1 / param2);
}

// 数组处理测试
void test_array_processing(int arr[], int size) {
    printf("=== 数组处理函数测试 ===\n");
    printf("原始数组: ");
    print_array(arr, size);
    printf("\n");
    
    // 打印原始统计
    print_array_stats(arr, size);
    
    // 调用你的函数
    // process_array(arr, size);
    
    // 示例：每个元素乘以2
    for (int i = 0; i < size; i++) {
        arr[i] = arr[i] * 2;
    }
    
    printf("\n处理后数组: ");
    print_array(arr, size);
    printf("\n");
    
    // 打印处理后统计
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    double mean = (double)sum / size;
    double stddev = calculate_stddev(arr, size, mean);
    
    printf("处理后统计:\n");
    printf("  新和值: %d\n", sum);
    printf("  新均值: %.2f\n", mean);
    printf("  标准差: %.2f\n", stddev);
}

// 字符串处理测试
void test_string_processing(char str[]) {
    printf("=== 字符串处理函数测试 ===\n");
    printf("原始字符串: \"%s\"\n", str);
    printf("字符串长度: %zu\n", strlen(str));
    
    // 调用你的函数
    // process_string(str);
    
    // 示例：转换为大写
    int len = strlen(str);
    for (int i = 0; i < len; i++) {
        if (str[i] >= 'a' && str[i] <= 'z') {
            str[i] = str[i] - 'a' + 'A';
        }
    }
    
    printf("处理后字符串: \"%s\"\n", str);
    
    // 字符统计
    int upper = 0, lower = 0, digits = 0, others = 0;
    for (int i = 0; i < len; i++) {
        if (str[i] >= 'A' && str[i] <= 'Z') upper++;
        else if (str[i] >= 'a' && str[i] <= 'z') lower++;
        else if (str[i] >= '0' && str[i] <= '9') digits++;
        else others++;
    }
    
    printf("字符统计: 大写=%d, 小写=%d, 数字=%d, 其他=%d\n", upper, lower, digits, others);
}

// 自定义测试
void test_custom() {
    printf("=== 自定义测试 ===\n");
    
    // 在这里添加你的自定义测试逻辑
    // 示例：读取自定义输入格式
    int a, b, c;
    if (scanf("%d %d %d", &a, &b, &c) == 3) {
        printf("读取到三个数字: %d, %d, %d\n", a, b, c);
        printf("最大值: %d\n", (a > b ? (a > c ? a : c) : (b > c ? b : c)));
        printf("最小值: %d\n", (a < b ? (a < c ? a : c) : (b < c ? b : c)));
        printf("平均值: %.2f\n", (a + b + c) / 3.0);
    } else {
        printf("需要输入三个数字，用空格分隔\n");
    }
}

// ================================
// 主函数 - 配置测试类型
// ================================

int main() {
    printf("代码回灌测试模板\n");
    printf("==================\n\n");
    
    // 配置测试类型 (修改这里来切换测试)
    test_type_t test_type = TEST_ARRAY_INPUT;
    
    // 读取输入数据
    printf("请输入测试数据:\n");
    
    switch (test_type) {
        case TEST_SINGLE_PARAM: {
            int param;
            if (scanf("%d", &param) == 1) {
                test_single_param(param);
            } else {
                printf("错误: 需要输入一个整数\n");
                return 1;
            }
            break;
        }
        
        case TEST_DOUBLE_PARAM: {
            int param1, param2;
            if (scanf("%d %d", &param1, &param2) == 2) {
                test_double_param(param1, param2);
            } else {
                printf("错误: 需要输入两个整数，用空格分隔\n");
                return 1;
            }
            break;
        }
        
        case TEST_ARRAY_INPUT: {
            int data[1000];
            int count = 0;
            
            // 读取任意数量的整数直到文件结束或达到最大值
            while (scanf("%d", &data[count]) == 1 && count < 1000) {
                count++;
            }
            
            if (count > 0) {
                test_array_processing(data, count);
            } else {
                printf("错误: 需要输入至少一个整数\n");
                return 1;
            }
            break;
        }
        
        case TEST_CUSTOM: {
            test_custom();
            break;
        }
        
        default:
            printf("错误: 未知的测试类型\n");
            return 1;
    }
    
    printf("\n测试完成\n");
    return 0;
}

// ================================
// 使用说明
// ================================

/*
使用步骤：

1. 在"要测试的函数定义"区域添加你的函数
   例如：
   int my_square(int x) {
       return x * x;
   }

2. 在对应的测试函数中调用你的函数
   例如在test_single_param中：
   int result = my_square(param);

3. 修改main()中的test_type来选择测试类型：
   - TEST_SINGLE_PARAM: 单参数测试
   - TEST_DOUBLE_PARAM: 双参数测试  
   - TEST_ARRAY_INPUT: 数组处理测试
   - TEST_CUSTOM: 自定义测试

4. 编译运行：
   gcc -o test_template test_template.c -lm
   ./test_template

5. 输入测试数据：
   单参数: 5
   双参数: 3 7
   数组: 1 2 3 4 5 (按Ctrl+D结束输入)

注意事项：
- 确保输入格式与测试类型匹配
- 函数返回值和参数类型要一致
- 数组测试最大支持1000个元素
- 可以根据需要修改最大值限制
*/