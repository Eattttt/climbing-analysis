COACH_SYSTEM_PROMPT = """你是一位拥有15年以上经验的专业攀岩教练。你的专长是技术分析和动作纠正。

你的分析风格：
- 鼓励为主，但诚实指出问题
- 每次重点指出2-3个最关键的改进点
- 引用具体的视频时间点
- 提供可执行的训练建议和练习方法
- 使用专业的攀岩术语（中文）

你需要分析的术语：
- 重心、把点、脚点、手点
- 动态、静态、死点
- 旗式、折膝、撑开、翻越
- 身体张力、核心收紧
- 前臂力量、握力
- 路线阅读、动作节奏

请用中文回复，语言专业但易懂。"""


def build_coach_message(
    duration: float,
    movements: list[dict],
    biomechanics_feedback: list[dict],
    joint_angle_stats: dict,
) -> str:
    lines = ["## 攀岩视频分析数据\n"]
    lines.append(f"**视频时长**: {duration:.1f}秒\n")

    if movements:
        lines.append("### 检测到的动作")
        for m in movements:
            lines.append(f"- {m.get('label_cn', m['type'])}: 第{m['start_frame']}-{m['end_frame']}帧 (置信度: {m['confidence']:.0%})")
        lines.append("")

    if biomechanics_feedback:
        lines.append("### 生物力学分析")
        for fb in biomechanics_feedback:
            icon = {"good": "✅", "info": "ℹ️", "warning": "⚠️", "critical": "🔴"}.get(fb["severity"], "")
            lines.append(f"- {icon} **{fb['title']}**: {fb['description']}")
        lines.append("")

    if joint_angle_stats:
        lines.append("### 关节角度统计")
        for joint, stats in joint_angle_stats.items():
            lines.append(f"- {joint}: 最小{stats['min']:.0f}° 最大{stats['max']:.0f}° 平均{stats['avg']:.0f}°")

    lines.append("\n请根据以上数据提供专业的攀岩技术分析和改进建议。")
    return "\n".join(lines)
