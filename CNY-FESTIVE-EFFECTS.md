# 🎊 中国农历新年节日特效

为指定的 HTML div 元素（id="index1"）生成的中国农历新年节日特效代码库。

## 📁 文件结构

```
cny-festive-effects.html        - 完整演示页面（推荐先看这个）
cny-festive-effects.js          - JavaScript 模块文件
cny-integration-example.html    - 集成示例
cny-quick-snippet.html          - 快速代码片段
CNY-EFFECTS-README.md           - 详细文档
中国新年特效-使用指南.txt        - 中文快速指南
```

## ✨ 特效功能

| 特效 | 描述 | 可配置 |
|------|------|--------|
| 🎆 **烟花/爆竹** | 爆炸性的彩色粒子动画 | ✅ |
| 🧧 **红包飘落** | 可点击的红包从上往下飘落 | ✅ |
| 🏮 **灯笼闪烁** | 传统红灯笼呼吸灯效果 | ✅ |
| 🎊 **纸屑飘落** | 多彩节日纸屑动画 | ✅ |
| 📝 **祝福文字** | 渐入渐出的金色祝福语 | ✅ |

## 🚀 3 分钟快速开始

### 方法 1：查看演示

```bash
# 在浏览器中打开
open cny-festive-effects.html
```

或者双击 `cny-festive-effects.html` 文件。

### 方法 2：集成到现有项目

```html
<!-- 1. 引入 JS 文件 -->
<script src="cny-festive-effects.js"></script>

<!-- 2. 准备容器 -->
<div id="index1">
    <!-- 你的内容 -->
</div>

<!-- 3. 初始化 -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const effects = new CNYFestiveEffects('index1');
});
</script>
```

### 方法 3：快速复制粘贴

1. 打开 `cny-quick-snippet.html`
2. 复制全部内容
3. 粘贴到你的 HTML 文件中
4. 完成！

## ⚙️ 配置示例

```javascript
const effects = new CNYFestiveEffects('index1', {
    // 开关控制
    enableFireworks: true,        // 烟花
    enableRedEnvelopes: true,     // 红包
    enableLanterns: true,         // 灯笼
    enableConfetti: true,         // 纸屑
    enableBlessings: true,        // 祝福语
    
    // 频率控制
    fireworksFrequency: 0.02,     // 烟花频率 (0-1)
    redEnvelopeInterval: 3000,    // 红包间隔(ms)
    confettiInterval: 400,        // 纸屑间隔(ms)
    blessingInterval: 8000,       // 祝福语间隔(ms)
    
    // 自定义内容
    customBlessings: [
        '新年快乐',
        '恭喜发财',
        '万事如意'
    ]
});
```

## 🎮 API 方法

```javascript
effects.triggerFireworks(5);        // 放5个烟花
effects.addBlessing('龙年大吉');     // 显示自定义祝福
effects.pause();                     // 暂停
effects.resume();                    // 恢复
effects.toggle();                    // 切换暂停/继续
effects.destroy();                   // 销毁并清理
```

## 📱 移动端优化

```javascript
const isMobile = /Android|webOS|iPhone|iPad/i.test(navigator.userAgent);

const effects = new CNYFestiveEffects('index1', {
    enableFireworks: !isMobile,      // 移动端禁用烟花
    fireworksFrequency: 0.01,        // 降低频率
    redEnvelopeInterval: 5000,       // 延长间隔
    enableLanterns: !isMobile        // 移动端禁用灯笼
});
```

## 🎨 样式自定义

```css
/* 自定义红包 */
.cny-red-envelope {
    width: 60px !important;
    height: 80px !important;
}

/* 自定义祝福语 */
.cny-blessing-text {
    font-size: 60px !important;
    color: #ff0000 !important;
}

/* 自定义灯笼 */
.cny-lantern-body {
    background: radial-gradient(ellipse at center, #ff6600 0%, #cc3300 100%) !important;
}
```

## 💡 使用场景示例

### 场景 1：节日横幅

```html
<div id="festival-banner" style="height: 300px; position: relative;">
    <h1>新年快乐</h1>
</div>
<script>
    new CNYFestiveEffects('festival-banner', {
        enableLanterns: false
    });
</script>
```

### 场景 2：按钮触发

```html
<button onclick="effects.triggerFireworks()">🎆 放烟花</button>
<button onclick="effects.addBlessing()">🧧 显示祝福</button>
```

### 场景 3：定时特效

```javascript
const effects = new CNYFestiveEffects('index1');

// 每10秒触发特殊效果
setInterval(() => {
    effects.triggerFireworks(3);
    effects.addBlessing();
}, 10000);
```

## 🌐 浏览器兼容性

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 11+
- ✅ Edge 79+
- ✅ 移动浏览器
- ❌ IE（不支持）

## 📦 文件大小

- **cny-festive-effects.js**: ~17 KB (未压缩)
- **cny-quick-snippet.html**: ~11 KB (压缩版)

轻量级实现，不影响页面性能。

## 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| 特效不显示 | 检查容器ID、高度、position属性 |
| 性能卡顿 | 降低频率、禁用部分特效 |
| 样式冲突 | 使用!important，检查z-index |

详细故障排除请查看 `CNY-EFFECTS-README.md`

## 📚 文档

- **快速开始**: 本文件
- **详细文档**: `CNY-EFFECTS-README.md`
- **中文指南**: `中国新年特效-使用指南.txt`
- **示例代码**: `cny-integration-example.html`

## 🎯 技术特点

- ✅ **原生实现** - 纯 HTML/CSS/JavaScript，无框架依赖
- ✅ **轻量级** - 总体积小于 20KB
- ✅ **高性能** - 优化的动画和渲染
- ✅ **响应式** - 自动适应容器大小
- ✅ **可配置** - 丰富的配置选项
- ✅ **易集成** - 三种集成方式，简单快捷
- ✅ **可定制** - 支持样式和内容自定义

## 🎊 效果预览

打开 `cny-festive-effects.html` 即可查看所有特效的实时演示。

页面包含：
- 🎆 自动触发的随机烟花
- 🧧 持续飘落的可点击红包
- 🏮 四角闪烁的传统灯笼
- 🎊 多彩旋转的节日纸屑
- 📝 定时显示的祝福文字
- 🎮 交互式控制面板

## 📝 代码示例

### 基础使用

```html
<!DOCTYPE html>
<html>
<head>
    <script src="cny-festive-effects.js"></script>
</head>
<body>
    <div id="index1" style="min-height: 100vh;">
        <h1>新年快乐！</h1>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            new CNYFestiveEffects('index1');
        });
    </script>
</body>
</html>
```

### 高级使用

```html
<script>
// 创建实例并保存引用
const effects = new CNYFestiveEffects('index1', {
    enableFireworks: true,
    enableRedEnvelopes: true,
    enableLanterns: true,
    enableConfetti: false,
    enableBlessings: true,
    fireworksFrequency: 0.03,
    customBlessings: ['龙年大吉', '财源滚滚']
});

// 监听用户事件
document.getElementById('celebrate').addEventListener('click', () => {
    effects.triggerFireworks(5);
    effects.addBlessing('恭喜发财');
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    effects.destroy();
});
</script>
```

## 🎉 开始使用

1. 选择一个文件开始：
   - 想看效果 → 打开 `cny-festive-effects.html`
   - 要集成项目 → 使用 `cny-festive-effects.js`
   - 求快速方案 → 复制 `cny-quick-snippet.html`

2. 查看文档：
   - 详细 API → `CNY-EFFECTS-README.md`
   - 中文快速指南 → `中国新年特效-使用指南.txt`

3. 参考示例：
   - 集成示例 → `cny-integration-example.html`

## 📄 许可证

MIT License - 可自由使用和修改

---

**祝您新年快乐，万事如意！🎊🎉🎆**
