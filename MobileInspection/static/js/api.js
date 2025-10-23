/**
 * 获取线缆数据
 * @param {string} cableId - 线缆ID
 * @returns {Promise<Object|null>} 线缆数据或null
 */
async function fetchCableData(cableId) {
    try {
        // 发送API请求获取线缆数据
        const response = await fetch(`/api/cable/${cableId}`);
        
        // 检查响应状态
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 解析JSON响应
        const data = await response.json();
        
        // 检查是否有错误
        if (data.error) {
            console.error('API Error:', data.error);
            return null;
        }
        
        return data;
    } catch (error) {
        // 错误处理
        console.error('Fetch error:', error);
        return null;
    }
}

/**
 * 提交巡检记录
 * @param {Object} data - 巡检数据
 * @returns {Promise<Object>} API响应
 */
async function submitInspection(data) {
    try {
        // 发送POST请求提交巡检记录
        const response = await fetch('/api/inspection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        // 检查响应状态
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 解析JSON响应
        return await response.json();
    } catch (error) {
        // 错误处理
        console.error('Submit error:', error);
        return { error: error.message };
    }
}

/**
 * 生成二维码
 * @param {string} cableId - 线缆ID
 * @returns {Promise<Object>} 二维码数据
 */
async function generateQRCode(cableId) {
    try {
        // 发送API请求生成二维码
        const response = await fetch(`/api/qrcode/${cableId}`);
        
        // 检查响应状态
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 解析JSON响应
        return await response.json();
    } catch (error) {
        // 错误处理
        console.error('QR Code error:', error);
        return { error: error.message };
    }
}