# 中国农历新年节日特效使用指南

## 📋 概述

这是一个轻量级的中国农历新年节日特效库，使用原生 HTML/CSS/JavaScript 实现，无需任何框架依赖。包含烟花、红包、灯笼、纸屑和祝福语等多种节日特效。

## ✨ 功能特性

1. **烟花/爆竹效果** - 动态粒子爆炸动画，支持多彩烟花
2. **红包飘落** - 可点击的红包从顶部飘落，点击触发烟花
3. **灯笼闪烁** - 四个方向的传统红灯笼，带呼吸灯效果
4. **纸屑飘落** - 多种形状和颜色的节日纸屑
5. **祝福语动画** - 渐入渐出的金色祝福文字

## 📦 文件说明

- `cny-festive-effects.html` - 完整的演示页面
- `cny-festive-effects.js` - 独立的 JavaScript 模块
- `CNY-EFFECTS-README.md` - 本使用文档

## 🚀 快速开始

### 方法 1：直接使用完整 HTML 文件

1. 打开 `cny-festive-effects.html` 即可查看所有特效
2. 可以直接在浏览器中运行，无需服务器

### 方法 2：集成到现有项目

#### 步骤 1：引入 JavaScript 文件

在你的 HTML 文件中引入 JavaScript 模块：

```html
<script src="cny-festive-effects.js"></script>
```

#### 步骤 2：准备目标容器

确保你的 HTML 中有一个 id 为 `index1` 的容器元素：

```html
<div id="index1">
    <!-- 你的页面内容 -->
</div>
```

#### 步骤 3：初始化特效

在页面加载完成后初始化特效：

```html
<script>
    // 页面加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        const effects = new CNYFestiveEffects('index1');
    });
</script>
```

## ⚙️ 配置选项

可以通过传入配置对象来自定义特效：

```javascript
const effects = new CNYFestiveEffects('index1', {
    enableFireworks: true,        // 是否启用烟花 (默认: true)
    enableRedEnvelopes: true,     // 是否启用红包 (默认: true)
    enableLanterns: true,         // 是否启用灯笼 (默认: true)
    enableConfetti: true,         // 是否启用纸屑 (默认: true)
    enableBlessings: true,        // 是否启用祝福语 (默认: true)
    fireworksFrequency: 0.02,     // 烟花频率 0-1 (默认: 0.02)
    redEnvelopeInterval: 3000,    // 红包生成间隔，毫秒 (默认: 3000)
    confettiInterval: 400,        // 纸屑生成间隔，毫秒 (默认: 400)
    blessingInterval: 8000,       // 祝福语间隔，毫秒 (默认: 8000)
    customBlessings: [            // 自定义祝福语 (可选)
        '新年快乐',
        '恭喜发财',
        '万事如意'
    ]
});
```

## 🎮 API 方法

### 手动触发烟花

```javascript
effects.triggerFireworks(3);  // 参数：烟花数量，默认 3
```

### 显示祝福语

```javascript
effects.addBlessing();              // 随机祝福语
effects.addBlessing('龙年大吉');    // 自定义祝福语
```

### 暂停特效

```javascript
effects.pause();
```

### 恢复特效

```javascript
effects.resume();
```

### 切换暂停/继续

```javascript
effects.toggle();  // 返回当前状态：true=运行，false=暂停
```

### 销毁特效

```javascript
effects.destroy();  // 清理所有特效元素和定时器
```

## 📝 使用示例

### 示例 1：基础使用

```html
<!DOCTYPE html>
<html>
<head>
    <title>新年快乐</title>
    <script src="cny-festive-effects.js"></script>
</head>
<body>
    <div id="index1" style="min-height: 100vh; background: #1a1a2e;">
        <h1 style="text-align: center; color: gold; padding-top: 100px;">
            🎉 恭喜发财，新年快乐！🎉
        </h1>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const effects = new CNYFestiveEffects('index1');
        });
    </script>
</body>
</html>
```

### 示例 2：自定义配置

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    const effects = new CNYFestiveEffects('index1', {
        enableFireworks: true,
        enableRedEnvelopes: true,
        enableLanterns: true,
        enableConfetti: false,  // 禁用纸屑
        enableBlessings: true,
        fireworksFrequency: 0.05,  // 更频繁的烟花
        redEnvelopeInterval: 2000,  // 红包间隔缩短为 2 秒
        customBlessings: [
            '恭喜发财', '新年快乐', '万事如意',
            '龙年大吉', '心想事成', '财源广进'
        ]
    });

    // 添加控制按钮
    document.getElementById('triggerBtn').addEventListener('click', function() {
        effects.triggerFireworks(5);
        effects.addBlessing('龙年大吉');
    });
});
</script>
```

### 示例 3：动态控制

```html
<button onclick="effects.toggle()">暂停/继续</button>
<button onclick="effects.triggerFireworks()">放烟花</button>
<button onclick="effects.addBlessing()">显示祝福</button>
<button onclick="effects.destroy()">清除特效</button>

<script>
    let effects;
    document.addEventListener('DOMContentLoaded', function() {
        effects = new CNYFestiveEffects('index1');
    });
</script>
```

### 示例 4：多容器使用

```html
<div id="header-effects" style="height: 300px; position: relative;"></div>
<div id="footer-effects" style="height: 300px; position: relative;"></div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // 头部特效 - 只要烟花和祝福语
    const headerEffects = new CNYFestiveEffects('header-effects', {
        enableFireworks: true,
        enableRedEnvelopes: false,
        enableLanterns: false,
        enableConfetti: false,
        enableBlessings: true
    });

    // 底部特效 - 只要红包和纸屑
    const footerEffects = new CNYFestiveEffects('footer-effects', {
        enableFireworks: false,
        enableRedEnvelopes: true,
        enableLanterns: false,
        enableConfetti: true,
        enableBlessings: false
    });
});
</script>
```

## 🎨 样式定制

所有样式类都使用 `cny-` 前缀，可以通过 CSS 覆盖来自定义：

```css
/* 自定义红包样式 */
.cny-red-envelope {
    width: 60px !important;
    height: 80px !important;
}

/* 自定义祝福语样式 */
.cny-blessing-text {
    font-size: 60px !important;
    color: #ff4444 !important;
}

/* 自定义灯笼样式 */
.cny-lantern-body {
    background: radial-gradient(ellipse at center, #ff0000 0%, #880000 100%) !important;
}
```

## ⚡ 性能优化建议

1. **移动设备优化**：在移动设备上减少特效数量
   ```javascript
   const isMobile = /Android|webOS|iPhone|iPad/i.test(navigator.userAgent);
   const effects = new CNYFestiveEffects('index1', {
       fireworksFrequency: isMobile ? 0.01 : 0.02,
       redEnvelopeInterval: isMobile ? 5000 : 3000,
       confettiInterval: isMobile ? 800 : 400
   });
   ```

2. **按需启用**：只启用需要的特效
3. **及时销毁**：页面切换时调用 `destroy()` 方法清理资源

## 🌐 浏览器兼容性

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 11+
- ✅ Edge 79+
- ✅ 移动端浏览器

## 📱 响应式设计

特效会自动适应容器大小，支持响应式布局。确保容器元素有合适的宽度和高度。

## 🔧 故障排除

### 问题 1：特效不显示

**解决方案**：
- 确认容器元素存在且 ID 正确
- 检查容器是否有足够的高度（建议至少 300px）
- 确保 JavaScript 在 DOM 加载完成后执行

### 问题 2：性能问题

**解决方案**：
- 降低特效频率
- 禁用部分特效
- 减少同时显示的元素数量

### 问题 3：样式冲突

**解决方案**：
- 所有样式类都使用 `cny-` 前缀，避免冲突
- 使用 `!important` 覆盖样式
- 检查 z-index 层级

## 📄 许可证

本项目使用 MIT 许可证，可自由使用和修改。

## 🎉 更新日志

### v1.0.0 (2025-01-21)
- ✨ 初始版本发布
- 🎆 烟花效果
- 🧧 红包飘落
- 🏮 灯笼闪烁
- 🎊 纸屑飘落
- 📝 祝福语动画

## 💡 建议与反馈

如有问题或建议，欢迎反馈！

---

**祝您新年快乐，万事如意！🎊🎉**
