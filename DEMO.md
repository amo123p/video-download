# 🧧 春节特效演示页面

完整的中国农历新年节日特效演示 - 可在线预览的独立 HTML 页面

## 📋 目录

- [在线预览](#在线预览)
- [特效展示](#特效展示)
- [使用方法](#使用方法)
- [技术特点](#技术特点)
- [集成指南](#集成指南)
- [浏览器支持](#浏览器支持)

## 🌐 在线预览

### 方式一：直接打开本地文件
```bash
# 克隆仓库后，直接在浏览器中打开
open preview.html  # macOS
start preview.html  # Windows
xdg-open preview.html  # Linux
```

### 方式二：通过 GitHub Pages 预览
如果已部署到 GitHub Pages，可以通过以下链接访问：
```
https://[你的用户名].github.io/[仓库名]/preview.html
```

### 方式三：通过 GitHub 原始内容预览
使用 [htmlpreview.github.io](https://htmlpreview.github.io/) 服务：
```
https://htmlpreview.github.io/?https://github.com/[用户名]/[仓库名]/blob/[分支名]/preview.html
```

## ✨ 特效展示

### 1. 🎆 烟花特效
- **描述**：绚丽的烟花绽放动画，使用 Canvas 2D 技术实现
- **特点**：
  - 多种颜色随机组合（红、金、橙、粉、绿、青、紫）
  - 粒子物理效果（重力、速度衰减）
  - 自动随机触发 + 手动控制
  - 流畅的拖尾效果

### 2. 🧧 红包飘落
- **描述**：可交互的红包动画，从顶部飘落
- **特点**：
  - 旋转飘落动画
  - 点击触发烟花和祝福语
  - 鼠标悬停放大效果
  - 随机位置和速度

### 3. 🏮 灯笼闪烁
- **描述**：传统中国灯笼装饰
- **特点**：
  - 呼吸灯光效果（渐明渐暗）
  - 轻微摆动动画
  - 四个角落固定位置
  - 春、福、喜、财四字装饰

### 4. 🎊 纸屑飘落
- **描述**：彩色纸屑连续飘落动画
- **特点**：
  - 多种形状（方形、圆形、三角形）
  - 旋转飘落效果
  - 渐变透明度
  - 持续生成

### 5. 💬 祝福语特效
- **描述**：新年祝福文字动画
- **特点**：
  - 12 种传统祝福语随机显示
  - 渐入渐出动画
  - 金色发光文字效果
  - 随机位置出现

## 🎮 使用方法

### 交互控制

页面右上角有控制面板，提供以下功能：

1. **🎆 放烟花**：立即触发 3 连发烟花效果
2. **💬 显示祝福**：随机显示一条祝福语
3. **⏯️ 暂停/继续**：暂停或继续所有自动特效
4. **🎇 烟花秀**：触发 10 连发烟花大秀

### 隐藏彩蛋

- 点击飘落的红包会触发烟花 + 祝福语双重惊喜

## 🛠 技术特点

### 完全独立
- ✅ **零外部依赖**：无需引入任何第三方库
- ✅ **单文件完整**：所有代码（HTML + CSS + JavaScript）集成在一个文件中
- ✅ **即开即用**：直接在浏览器中打开即可运行

### 技术栈
- **HTML5**：语义化标签
- **CSS3**：
  - 动画（@keyframes）
  - 渐变（linear-gradient, radial-gradient）
  - 变换（transform）
  - 滤镜（backdrop-filter）
  - 响应式设计（@media queries）
- **JavaScript ES6+**：
  - 类（Class）
  - Canvas 2D API
  - requestAnimationFrame
  - 事件监听
  - 定时器管理

### 性能优化
- 粒子生命周期管理（自动清理）
- Canvas 双缓冲技术
- DOM 元素定时清理
- 响应式画布尺寸调整

### 兼容性
- 响应式设计，支持移动端和桌面端
- 渐进增强，优雅降级
- 现代浏览器全面支持

## 📦 集成指南

### 快速集成到你的项目

#### 方法 1：复制整个文件
直接将 `preview.html` 复制到你的项目中使用。

#### 方法 2：提取核心代码
如果你已经有自己的页面，可以提取特效代码：

```html
<!-- 1. 在你的页面中添加目标容器 -->
<div id="index1">
  <!-- 你的内容 -->
</div>

<!-- 2. 复制 <style> 标签中的 CSS（从 preview.html） -->
<style>
  /* 复制所有特效相关的 CSS 样式 */
</style>

<!-- 3. 复制 <script> 标签中的 JavaScript（从 preview.html） -->
<script>
  // 复制 CNYEffects 类和初始化代码
</script>
```

#### 方法 3：提取为独立 JS 模块
可以将 JavaScript 代码提取为独立的 `.js` 文件：

```javascript
// cny-effects.js
class CNYEffects {
  // ... 复制类的完整代码
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
  window.CNYEffects = new CNYEffects('index1');
});
```

然后在 HTML 中引用：
```html
<script src="cny-effects.js"></script>
```

### 自定义配置

#### 修改祝福语
编辑 `CNYEffects` 类中的 `blessings` 数组：

```javascript
this.blessings = [
    '你的祝福语 1',
    '你的祝福语 2',
    // ... 更多祝福语
];
```

#### 调整特效频率
修改 `setInterval` 中的时间参数（单位：毫秒）：

```javascript
// 红包飘落频率（默认 3000ms = 3秒）
setInterval(() => { ... }, 3000);

// 纸屑生成频率（默认 400ms）
setInterval(() => { ... }, 400);

// 祝福语显示频率（默认 8000ms = 8秒）
setInterval(() => { ... }, 8000);
```

#### 修改颜色主题
编辑 CSS 变量或直接修改颜色值：

```css
/* 红包颜色 */
.red-envelope {
    background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
}

/* 烟花颜色 */
const colors = ['#ff4444', '#ffd700', '#ff6b00', ...];
```

#### 调整灯笼位置
修改 `createLanterns()` 方法中的 `positions` 数组：

```javascript
const positions = [
    { top: '5%', left: '10%' },   // 左上
    { top: '5%', right: '10%' },  // 右上
    { top: '40%', left: '5%' },   // 左中
    { top: '40%', right: '5%' }   // 右中
];
```

## 🌏 浏览器支持

| 浏览器 | 最低版本 | 支持状态 |
|--------|---------|---------|
| Chrome | 60+ | ✅ 完全支持 |
| Firefox | 55+ | ✅ 完全支持 |
| Safari | 12+ | ✅ 完全支持 |
| Edge | 79+ | ✅ 完全支持 |
| Opera | 47+ | ✅ 完全支持 |
| iOS Safari | 12+ | ✅ 完全支持 |
| Android Chrome | 60+ | ✅ 完全支持 |

### 需要的浏览器特性
- Canvas 2D Context
- ES6 Class
- CSS3 Animations
- CSS3 Transforms
- requestAnimationFrame
- backdrop-filter（可选，用于毛玻璃效果）

## 📝 使用场景

适用于以下场景：

- 🎉 **节日活动页面**：春节、新年等节日主题页面
- 🎊 **营销活动**：红包雨、抽奖活动等营销页面
- 🏮 **企业官网**：春节期间的官网装饰
- 🎆 **H5 页面**：移动端节日主题页面
- 🧧 **电商平台**：年货节、春节促销活动页面

## 🔧 故障排除

### 特效不显示
1. 检查容器 ID 是否为 `index1`
2. 确保 JavaScript 代码在 DOM 加载完成后执行
3. 打开浏览器控制台查看错误信息

### 性能问题
1. 减少特效生成频率
2. 降低烟花粒子数量
3. 在低端设备上禁用部分特效

### 响应式问题
1. 确保容器有合适的宽高
2. 检查 CSS 媒体查询是否生效
3. 在移动设备上测试触摸事件

## 📄 许可证

本项目代码可自由使用于个人和商业项目。

## 🎁 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- GitHub Issues
- 项目讨论区

---

**祝你新年快乐，万事如意！🎉🧧🏮**
