// 全局变量
let scannerActive = false;  // 扫描器激活状态
let currentCableId = null;  // 当前扫描到的线缆ID

/**
 * 初始化扫描器
 * 配置并启动二维码扫描
 */
function initScanner() {
    // 使用Quagga库初始化扫描器
    Quagga.init({
        // 输入流配置
        inputStream: {
            name: "Live",  // 流名称
            type: "LiveStream",  // 实时流
            target: document.querySelector('#scanner-container'),  // 目标容器
            constraints: {
                width: 480,  // 宽度
                height: 320,  // 高度
                facingMode: "environment"  // 使用后置摄像头
            },
        },
        // 解码器配置
        decoder: {
            readers: ["qr_code_reader"],  // 只使用二维码阅读器
            debug: {
                drawBoundingBox: true,  // 绘制边界框
                showFrequency: true,  // 显示频率
                drawScanline: true,  // 绘制扫描线
                showPattern: true  // 显示模式
            }
        },
        // 定位器配置
        locator: {
            patchSize: "medium",  // 补丁大小
            halfSample: true  // 半采样
        }
    }, function(err) {
        if (err) {
            // 初始化失败处理
            console.error(err);
            document.getElementById('result').textContent = '初始化扫描器失败: ' + err.message;
            return;
        }
        
        // 初始化成功，启动扫描器
        console.log("扫描器初始化成功");
        Quagga.start();
        scannerActive = true;
        updateScannerButtons();
    });
    
    // 监听二维码检测事件
    Quagga.onDetected(function(result) {
        // 获取扫描到的二维码内容
        const code = result.codeResult.code;
        document.getElementById('result').textContent = '扫描到二维码: ' + code;
        
        // 从URL中提取线缆ID
        const matches = code.match(/cable\/([^\/]+)/);
        if (matches && matches[1]) {
            currentCableId = matches[1];
            // 跳转到线缆详情页
            window.location.href = `/cable/${currentCableId}`;
        } else {
            // 无效二维码处理
            document.getElementById('result').textContent = '无效的二维码: ' + code;
        }
    });
}

/**
 * 停止扫描器
 */
function stopScanner() {
    if (scannerActive) {
        // 停止扫描器
        Quagga.stop();
        scannerActive = false;
        updateScannerButtons();
        document.getElementById('result').textContent = '扫描已停止';
    }
}

/**
 * 更新扫描按钮状态
 */
function updateScannerButtons() {
    document.getElementById('start-scanner').disabled = scannerActive;
    document.getElementById('stop-scanner').disabled = !scannerActive;
}

/**
 * 初始化扫描器控制
 */
function initScannerControls() {
    // 绑定开始扫描按钮事件
    document.getElementById('start-scanner').addEventListener('click', initScanner);
    
    // 绑定停止扫描按钮事件
    document.getElementById('stop-scanner').addEventListener('click', stopScanner);
}

// 在scanner.js中添加模拟扫描函数
function simulateScan(cableId) {
    document.getElementById('result').textContent = '模拟扫描到二维码: ' + cableId;
    currentCableId = cableId;
    window.location.href = `/cable/${currentCableId}`;
}

// 在页面添加测试按钮
document.addEventListener('DOMContentLoaded', function() {
    // 添加模拟扫描按钮
    const testButtons = document.createElement('div');
    testButtons.innerHTML = `
        <h3>测试线缆</h3>
        <button onclick="simulateScan('CBL20230001')">CBL20230001</button>
        <button onclick="simulateScan('CBL20230002')">CBL20230002</button>
        <button onclick="simulateScan('CBL20230003')">CBL20230003</button>
        <button onclick="simulateScan('CBL20230004')">CBL20230004</button>
        <button onclick="simulateScan('CBL20230005')">CBL20230005</button>
        <button onclick="simulateScan('CBL20230006')">CBL20230006</button>
        <button onclick="simulateScan('CBL20230007')">CBL20230007</button>
        <button onclick="simulateScan('CBL20230008')">CBL20230008</button>
        <button onclick="simulateScan('CBL20230009')">CBL20230009</button>
        <button onclick="simulateScan('CBL20230010')">CBL20230010</button>
    `;
    document.querySelector('.scanner-section').appendChild(testButtons);
});