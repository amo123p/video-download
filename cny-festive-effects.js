/**
 * 中国农历新年节日特效模块
 * 版本: 1.0.0
 * 
 * 功能:
 * - 烟花/爆竹效果
 * - 红包飘落动画
 * - 灯笼闪烁
 * - 纸屑飘落
 * - 祝福语动画
 * 
 * 使用方法:
 * const effects = new CNYFestiveEffects('index1', options);
 */

class CNYFestiveEffects {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`容器 #${containerId} 未找到`);
            return;
        }

        // 合并配置选项
        this.options = {
            enableFireworks: true,      // 启用烟花
            enableRedEnvelopes: true,    // 启用红包
            enableLanterns: true,        // 启用灯笼
            enableConfetti: true,        // 启用纸屑
            enableBlessings: true,       // 启用祝福语
            fireworksFrequency: 0.02,    // 烟花频率 (0-1)
            redEnvelopeInterval: 3000,   // 红包生成间隔(毫秒)
            confettiInterval: 400,       // 纸屑生成间隔(毫秒)
            blessingInterval: 8000,      // 祝福语间隔(毫秒)
            customBlessings: null,       // 自定义祝福语数组
            ...options
        };

        this.isRunning = true;
        this.fireworksCanvas = null;
        this.fireworksCtx = null;
        this.particles = [];
        this.intervals = [];
        
        this.blessings = this.options.customBlessings || [
            '新年快乐', '恭喜发财', '万事如意', '龙年大吉',
            '心想事成', '福星高照', '吉祥如意', '财源广进',
            '步步高升', '阖家欢乐', '身体健康', '事业有成'
        ];

        this.init();
    }

    init() {
        // 注入样式
        this.injectStyles();

        // 确保容器具有相对定位
        if (getComputedStyle(this.container).position === 'static') {
            this.container.style.position = 'relative';
        }

        // 初始化各种效果
        if (this.options.enableFireworks) {
            this.initFireworksCanvas();
            this.startFireworksAnimation();
        }

        if (this.options.enableLanterns) {
            this.createLanterns();
        }

        if (this.options.enableRedEnvelopes) {
            this.startRedEnvelopes();
        }

        if (this.options.enableConfetti) {
            this.startConfetti();
        }

        if (this.options.enableBlessings) {
            this.startBlessings();
        }
    }

    injectStyles() {
        const styleId = 'cny-festive-effects-styles';
        if (document.getElementById(styleId)) return;

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            /* 烟花画布 */
            .cny-fireworks-canvas {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 997;
            }

            /* 红包样式 */
            .cny-red-envelope {
                position: absolute;
                width: 50px;
                height: 70px;
                background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
                border-radius: 5px;
                box-shadow: 0 5px 15px rgba(255, 68, 68, 0.5);
                pointer-events: auto;
                cursor: pointer;
                animation: cnyFall linear infinite;
                z-index: 1001;
            }

            .cny-red-envelope::before {
                content: '福';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #ffd700;
                font-size: 28px;
                font-weight: bold;
            }

            .cny-red-envelope::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 25px;
                background: linear-gradient(135deg, #cc0000 0%, #990000 100%);
                border-radius: 5px 5px 0 0;
            }

            @keyframes cnyFall {
                to {
                    transform: translateY(calc(100vh + 70px)) rotate(360deg);
                }
            }

            /* 灯笼样式 */
            .cny-lantern {
                position: absolute;
                width: 60px;
                height: 80px;
                z-index: 999;
            }

            .cny-lantern-body {
                width: 100%;
                height: 70px;
                background: radial-gradient(ellipse at center, #ff4444 0%, #cc0000 100%);
                border-radius: 50%;
                position: relative;
                box-shadow: 0 0 20px rgba(255, 68, 68, 0.8);
                animation: cnyLanternGlow 2s ease-in-out infinite alternate;
            }

            .cny-lantern-rope {
                position: absolute;
                top: -20px;
                left: 50%;
                width: 2px;
                height: 20px;
                background: #8B4513;
                transform: translateX(-50%);
            }

            .cny-lantern-tassel {
                position: absolute;
                bottom: -15px;
                left: 50%;
                width: 20px;
                height: 15px;
                background: linear-gradient(to bottom, #ffd700, #ffaa00);
                transform: translateX(-50%);
                clip-path: polygon(50% 0%, 0% 30%, 20% 100%, 80% 100%, 100% 30%);
            }

            .cny-lantern-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #ffd700;
                font-size: 20px;
                font-weight: bold;
            }

            @keyframes cnyLanternGlow {
                0%, 100% {
                    box-shadow: 0 0 20px rgba(255, 68, 68, 0.8), 0 0 40px rgba(255, 68, 68, 0.4);
                }
                50% {
                    box-shadow: 0 0 30px rgba(255, 68, 68, 1), 0 0 60px rgba(255, 68, 68, 0.6);
                }
            }

            /* 纸屑样式 */
            .cny-confetti {
                position: absolute;
                width: 10px;
                height: 10px;
                pointer-events: none;
                animation: cnyConfettiFall linear infinite;
                z-index: 998;
            }

            @keyframes cnyConfettiFall {
                to {
                    transform: translateY(calc(100vh + 20px)) rotate(720deg);
                    opacity: 0;
                }
            }

            /* 祝福语样式 */
            .cny-blessing-text {
                position: absolute;
                font-size: 48px;
                font-weight: bold;
                color: #ffd700;
                text-shadow: 
                    0 0 10px rgba(255, 215, 0, 0.8),
                    0 0 20px rgba(255, 215, 0, 0.6),
                    0 0 30px rgba(255, 215, 0, 0.4),
                    2px 2px 4px rgba(0, 0, 0, 0.8);
                animation: cnyBlessingFadeIn 3s ease-out forwards;
                z-index: 1002;
                pointer-events: none;
                white-space: nowrap;
            }

            @keyframes cnyBlessingFadeIn {
                0% {
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(0.5) translateY(-50px);
                }
                50% {
                    opacity: 1;
                    transform: translate(-50%, -50%) scale(1.2) translateY(0);
                }
                100% {
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(1) translateY(50px);
                }
            }
        `;
        document.head.appendChild(style);
    }

    initFireworksCanvas() {
        let canvas = this.container.querySelector('.cny-fireworks-canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.className = 'cny-fireworks-canvas';
            this.container.insertBefore(canvas, this.container.firstChild);
        }
        
        this.fireworksCanvas = canvas;
        this.fireworksCtx = canvas.getContext('2d');
        this.resizeCanvas();
        
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        if (!this.fireworksCanvas) return;
        this.fireworksCanvas.width = this.container.offsetWidth;
        this.fireworksCanvas.height = this.container.offsetHeight;
    }

    // 烟花效果
    createFirework(x, y) {
        const colors = ['#ff4444', '#ffd700', '#ff6b00', '#ff1493', '#00ff00', '#00ffff'];
        const particleCount = 80;
        
        for (let i = 0; i < particleCount; i++) {
            const angle = (Math.PI * 2 * i) / particleCount;
            const velocity = 2 + Math.random() * 3;
            
            this.particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * velocity,
                vy: Math.sin(angle) * velocity,
                life: 1,
                color: colors[Math.floor(Math.random() * colors.length)],
                size: 2 + Math.random() * 3
            });
        }
    }

    updateFireworks() {
        if (!this.fireworksCtx) return;
        
        this.fireworksCtx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.fireworksCtx.fillRect(0, 0, this.fireworksCanvas.width, this.fireworksCanvas.height);

        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.05; // 重力
            p.life -= 0.01;

            if (p.life <= 0) {
                this.particles.splice(i, 1);
                continue;
            }

            this.fireworksCtx.globalAlpha = p.life;
            this.fireworksCtx.fillStyle = p.color;
            this.fireworksCtx.beginPath();
            this.fireworksCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.fireworksCtx.fill();
        }

        this.fireworksCtx.globalAlpha = 1;
    }

    startFireworksAnimation() {
        const animate = () => {
            if (this.isRunning) {
                this.updateFireworks();
                
                // 随机触发烟花
                if (Math.random() < this.options.fireworksFrequency) {
                    const x = Math.random() * this.fireworksCanvas.width;
                    const y = Math.random() * this.fireworksCanvas.height * 0.6;
                    this.createFirework(x, y);
                }
            }
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }

    // 手动触发烟花
    triggerFireworks(count = 3) {
        for (let i = 0; i < count; i++) {
            setTimeout(() => {
                const x = Math.random() * this.fireworksCanvas.width;
                const y = 100 + Math.random() * 200;
                this.createFirework(x, y);
            }, i * 300);
        }
    }

    // 红包飘落效果
    createRedEnvelope() {
        const envelope = document.createElement('div');
        envelope.className = 'cny-red-envelope';
        envelope.style.left = Math.random() * (this.container.offsetWidth - 50) + 'px';
        envelope.style.top = '-70px';
        
        const duration = 8 + Math.random() * 4;
        envelope.style.animationDuration = duration + 's';
        envelope.style.animationDelay = Math.random() * 2 + 's';
        
        envelope.addEventListener('click', (e) => {
            e.target.style.animation = 'none';
            e.target.style.transition = 'all 0.5s';
            e.target.style.transform = 'scale(0) rotate(360deg)';
            e.target.style.opacity = '0';
            
            setTimeout(() => e.target.remove(), 500);
            
            // 点击红包时触发烟花
            if (this.options.enableFireworks) {
                const rect = e.target.getBoundingClientRect();
                const containerRect = this.container.getBoundingClientRect();
                this.createFirework(
                    rect.left - containerRect.left + 25, 
                    rect.top - containerRect.top + 35
                );
            }
        });
        
        this.container.appendChild(envelope);
        
        setTimeout(() => {
            if (envelope.parentNode) {
                envelope.remove();
            }
        }, duration * 1000 + 2000);
    }

    startRedEnvelopes() {
        const interval = setInterval(() => {
            if (this.isRunning) {
                this.createRedEnvelope();
            }
        }, this.options.redEnvelopeInterval);
        this.intervals.push(interval);
    }

    // 灯笼效果
    createLanterns() {
        const lanternTexts = ['春', '福', '喜', '财'];
        const positions = [
            { top: '5%', left: '10%' },
            { top: '5%', left: '85%' },
            { top: '40%', left: '5%' },
            { top: '40%', right: '5%' }
        ];

        positions.forEach((pos, index) => {
            const lantern = document.createElement('div');
            lantern.className = 'cny-lantern';
            Object.assign(lantern.style, pos);
            
            lantern.innerHTML = `
                <div class="cny-lantern-rope"></div>
                <div class="cny-lantern-body">
                    <div class="cny-lantern-text">${lanternTexts[index % lanternTexts.length]}</div>
                </div>
                <div class="cny-lantern-tassel"></div>
            `;
            
            this.container.appendChild(lantern);
        });
    }

    // 纸屑飘落效果
    createConfetti() {
        const confetti = document.createElement('div');
        confetti.className = 'cny-confetti';
        
        const colors = ['#ff4444', '#ffd700', '#ff6b00', '#ff1493'];
        const shapes = ['square', 'circle', 'triangle'];
        const shape = shapes[Math.floor(Math.random() * shapes.length)];
        
        confetti.style.left = Math.random() * this.container.offsetWidth + 'px';
        confetti.style.top = '-10px';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDuration = (6 + Math.random() * 4) + 's';
        confetti.style.animationDelay = Math.random() * 2 + 's';
        
        if (shape === 'circle') {
            confetti.style.borderRadius = '50%';
        } else if (shape === 'triangle') {
            confetti.style.width = '0';
            confetti.style.height = '0';
            confetti.style.backgroundColor = 'transparent';
            confetti.style.borderLeft = '5px solid transparent';
            confetti.style.borderRight = '5px solid transparent';
            confetti.style.borderBottom = '10px solid ' + colors[Math.floor(Math.random() * colors.length)];
        }
        
        this.container.appendChild(confetti);
        
        setTimeout(() => {
            if (confetti.parentNode) {
                confetti.remove();
            }
        }, 12000);
    }

    startConfetti() {
        const interval = setInterval(() => {
            if (this.isRunning) {
                this.createConfetti();
            }
        }, this.options.confettiInterval);
        this.intervals.push(interval);
    }

    // 祝福语效果
    addBlessing(customText = null) {
        const blessing = document.createElement('div');
        blessing.className = 'cny-blessing-text';
        blessing.textContent = customText || this.blessings[Math.floor(Math.random() * this.blessings.length)];
        
        blessing.style.left = (20 + Math.random() * 60) + '%';
        blessing.style.top = (30 + Math.random() * 40) + '%';
        
        this.container.appendChild(blessing);
        
        setTimeout(() => {
            if (blessing.parentNode) {
                blessing.remove();
            }
        }, 3000);
    }

    startBlessings() {
        const interval = setInterval(() => {
            if (this.isRunning) {
                this.addBlessing();
            }
        }, this.options.blessingInterval);
        this.intervals.push(interval);
    }

    // 暂停效果
    pause() {
        this.isRunning = false;
    }

    // 恢复效果
    resume() {
        this.isRunning = true;
    }

    // 切换效果开关
    toggle() {
        this.isRunning = !this.isRunning;
        return this.isRunning;
    }

    // 销毁所有效果
    destroy() {
        this.isRunning = false;
        this.particles = [];
        
        // 清除所有定时器
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals = [];
        
        // 清理所有特效元素
        const elements = this.container.querySelectorAll(
            '.cny-red-envelope, .cny-confetti, .cny-blessing-text, .cny-lantern, .cny-fireworks-canvas'
        );
        elements.forEach(el => el.remove());
    }
}

// 导出为全局变量（用于直接在HTML中引用）
if (typeof window !== 'undefined') {
    window.CNYFestiveEffects = CNYFestiveEffects;
}

// 支持 ES6 模块导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CNYFestiveEffects;
}
