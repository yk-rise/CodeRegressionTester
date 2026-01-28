"""
增强的差异显示模块
提供直观的差异可视化功能
"""

def create_enhanced_diff_display(result_widget, diff_text, result):
    """创建增强的差异显示内容"""
    if not result or not result.differences:
        return "未发现差异"
    
    content = []
    
    # 添加差异标题和统计
    content.append("═" * 60)
    content.append(f" 差异分析报告: {result.test_case}")
    content.append("═" * 60)
    content.append(f" 总体状态: {result.overall_status}")
    content.append(f" 相似度: {result.similarity_score:.3f}")
    content.append(f" 差异数量: {len(result.differences)}")
    content.append("")
    
    # 添加误差指标（如果有）
    if result.error_metrics:
        content.append("📊 数值误差分析:")
        content.append(f"   平均绝对误差: {result.error_metrics.mae:.2e}")
        content.append(f"   均方根误差: {result.error_metrics.rmse:.2e}")
        content.append(f"   最大误差: {result.error_metrics.max_error:.2e}")
        content.append(f"   相关系数: {result.error_metrics.correlation:.3f}")
        content.append("")
    
    # 按重要性分组差异
    critical_diffs = [d for d in result.differences if 'error' in d.content.lower() or 'fail' in d.content.lower()]
    warning_diffs = [d for d in result.differences if d.type == 'change']
    other_diffs = [d for d in result.differences if d not in critical_diffs + warning_diffs]
    
    content.append("🔍 关键差异 (需要立即关注):")
    if critical_diffs:
        for diff in critical_diffs[:3]:  # 只显示前3个关键差异
            content.append(f"   ❌ 行 {diff.line_number}: {diff.content[:50]}")
        if len(critical_diffs) > 3:
            content.append(f"   ... 还有 {len(critical_diffs) - 3} 个关键差异")
    else:
        content.append("   ✅ 无关键差异")
    content.append("")
    
    content.append("⚠️  修改差异:")
    if warning_diffs:
        for diff in warning_diffs[:5]:  # 显示前5个修改
            content.append(f"   🔄 行 {diff.line_number}: {diff.content[:40]}")
        if len(warning_diffs) > 5:
            content.append(f"   ... 还有 {len(warning_diffs) - 5} 个修改差异")
    else:
        content.append("   ✅ 无修改差异")
    content.append("")
    
    content.append("📍 其他差异:")
    if other_diffs:
        for diff in other_diffs[:3]:  # 显示前3个其他差异
            icon = "➕" if diff.type == 'addition' else "➖"
            content.append(f"   {icon} 行 {diff.line_number}: {diff.content[:30]}")
        if len(other_diffs) > 3:
            content.append(f"   ... 还有 {len(other_diffs) - 3} 个其他差异")
    else:
        content.append("   ✅ 无其他差异")
    content.append("")
    
    # 显示详细差异位置
    content.append("🎯 差异位置详情:")
    for i, diff in enumerate(result.differences[:5], 1):
        diff_type = {"addition": "新增", "deletion": "删除", "change": "修改"}.get(diff.type, "未知")
        icon = {"addition": "➕", "deletion": "➖", "change": "🔄"}.get(diff.type, "❓")
        
        content.append(f"  {i}. 行 {diff.line_number} [{icon} {diff_type}]")
        content.append(f"     内容: {diff.content}")
        if diff.context and len(diff.context) > 0:
            # 显示上下文的第一行
            context_lines = diff.context.split('\n')
            if context_lines:
                context_preview = context_lines[0].strip()
                if len(context_preview) > 60:
                    context_preview = context_preview[:57] + "..."
                content.append(f"     上下文: {context_preview}")
        content.append("")
    
    if len(result.differences) > 5:
        content.append(f"... 还有 {len(result.differences) - 5} 个差异未显示")
    
    # 添加输出对比（如果有）
    if hasattr(result, 'version_a_result') and hasattr(result, 'version_b_result'):
        if result.version_a_result.stdout and result.version_b_result.stdout:
            content.append("")
            content.append("📄 输出对比:")
            lines_a = result.version_a_result.stdout.splitlines()
            lines_b = result.version_b_result.stdout.splitlines()
            
            # 找出前5个不同的输出行
            diff_lines = []
            for i in range(min(5, len(lines_a), len(lines_b))):
                if lines_a[i].strip() != lines_b[i].strip():
                    diff_lines.append((i+1, lines_a[i], lines_b[i]))
            
            if diff_lines:
                content.append("   不同的输出行:")
                for line_num, line_a, line_b in diff_lines:
                    content.append(f"   行{line_num}:")
                    content.append(f"     版本A: {line_a}")
                    content.append(f"     版本B: {line_b}")
                    content.append("")
            else:
                content.append("   ✅ 输出完全相同")
    
    return "\n".join(content)

def create_side_by_side_diff(result):
    """创建并排差异显示"""
    if not result.differences:
        return "两个版本完全相同，无差异"
    
    # 这里可以实现更复杂的并排显示逻辑
    return create_enhanced_diff_display(None, None, result)

def get_diff_summary_html(result):
    """生成HTML格式的差异摘要"""
    if not result.differences:
        return "<p>✅ 无差异</p>"
    
    html = []
    html.append(f"<h3>📊 差异分析: {result.test_case}</h3>")
    html.append(f"<p><strong>状态:</strong> {result.overall_status} | ")
    html.append(f"<strong>相似度:</strong> {result.similarity_score:.3f} | ")
    html.append(f"<strong>差异数:</strong> {len(result.differences)}</p>")
    
    # 差异类型统计
    additions = sum(1 for d in result.differences if d.type == 'addition')
    deletions = sum(1 for d in result.differences if d.type == 'deletion')
    changes = sum(1 for d in result.differences if d.type == 'change')
    
    html.append("<div style='margin: 10px 0;'>")
    html.append("  <span style='background: #d4edda; padding: 2px 6px; margin-right: 5px;'>➕ 新增 {additions}</span>")
    html.append("  <span style='background: #f8d7da; padding: 2px 6px; margin-right: 5px;'>➖ 删除 {deletions}</span>")
    html.append("  <span style='background: #fff3cd; padding: 2px 6px;'>🔄 修改 {changes}</span>")
    html.append("</div>")
    
    # 显示关键差异
    critical_diffs = [d for d in result.differences if 'error' in d.content.lower() or 'fail' in d.content.lower()]
    if critical_diffs:
        html.append("<h4 style='color: #dc3545;'>🚨 关键差异:</h4>")
        html.append("<ul>")
        for diff in critical_diffs[:3]:
            html.append(f"<li><strong>行 {diff.line_number}:</strong> {diff.content[:100]}</li>")
        html.append("</ul>")
    
    return "".join(html)

def format_diff_for_display(diff_text, highlight_differences=True):
    """格式化差异文本以供显示"""
    if not highlight_differences or not diff_text:
        return diff_text
    
    lines = diff_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.startswith('-'):
            # 删除行 - 红色高亮
            formatted_lines.append(f'<span style="color: #dc3545; background: #f8d7da;">{line}</span>')
        elif line.startswith('+'):
            # 添加行 - 绿色高亮
            formatted_lines.append(f'<span style="color: #155724; background: #d4edda;">{line}</span>')
        elif line.startswith('@@'):
            # 文件头信息 - 蓝色
            formatted_lines.append(f'<span style="color: #0066cc; font-weight: bold;">{line}</span>')
        elif line.startswith(' '):
            # 上下文行 - 灰色
            formatted_lines.append(f'<span style="color: #6c757d;">{line}</span>')
        else:
            # 其他行
            formatted_lines.append(line)
    
    return "\n".join(formatted_lines)