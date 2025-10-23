// 全局变量
let currentCableId = null;  // 当前线缆ID
let submitHandlerBound = false; // 新增：标记是否已绑定事件

/**
 * 显示基本信息
 * @param {Object} info - 线缆基本信息
 */
function displayBasicInfo(info) {
    const basicInfoDiv = document.getElementById('basic-info');
    
    // 构建HTML内容
    basicInfoDiv.innerHTML = `
        <p><strong>线缆ID:</strong> ${info.cable_id}</p>
        <p><strong>规格型号:</strong> ${info.specification}</p>
        <p><strong>生产日期:</strong> ${new Date(info.production_date).toLocaleString()}</p>
        <p><strong>长度:</strong> ${info.length}米</p>
        <p><strong>当前状态:</strong> <span class="status-${info.status === '合格' ? 'good' : 'bad'}">${info.status}</span></p>
    `;
}

/**
 * 显示工艺流程数据
 * @param {Array} processes - 工艺流程数据数组
 */
function displayProcessData(processes) {
    const tbody = document.getElementById('process-data');
    tbody.innerHTML = '';  // 清空现有内容
    
    // 遍历并添加每行数据
    processes.forEach(process => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${process.process_name}</td>
            <td>${new Date(process.process_time).toLocaleString()}</td>
            <td>${process.operator_id}</td>
            <td>${process.machine_id}</td>
            <td>${JSON.stringify(process.parameters)}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * 显示检测数据
 * @param {Array} inspections - 检测数据数组
 */
function displayInspectionData(inspections) {
    const tbody = document.getElementById('inspection-data');
    tbody.innerHTML = '';  // 清空现有内容
    
    // 遍历并添加每行数据
    inspections.forEach(inspection => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${inspection.test_item}</td>
            <td>${new Date(inspection.inspection_time).toLocaleString()}</td>
            <td>${inspection.test_value}</td>
            <td>${inspection.standard_value}</td>
            <td class="status-${inspection.result === '合格' ? 'good' : 'bad'}">${inspection.result}</td>
            <td>${inspection.inspector_id}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * 显示库存数据
 * @param {Array} inventory - 库存数据数组
 */
function displayInventoryData(inventory) {
    const tbody = document.getElementById('inventory-data');
    tbody.innerHTML = '';  // 清空现有内容
    
    // 遍历并添加每行数据
    inventory.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.operation_type}</td>
            <td>${new Date(record.record_time).toLocaleString()}</td>
            <td>${record.location}</td>
            <td>${record.operator_id}</td>
            <td>${record.notes || ''}</td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * 切换标签页
 * @param {Event} evt - 事件对象
 * @param {string} tabName - 标签页名称
 */
function openTab(evt, tabName) {
    // 隐藏所有标签内容
    const tabcontents = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontents.length; i++) {
        tabcontents[i].style.display = "none";
    }
    
    // 移除所有标签的活动状态
    const tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    
    // 显示当前标签内容并设置活动状态
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

/**
 * 初始化UI
 */
/**
 * 初始化UI
 */
function initUI() {
    // 初始化标签页
    const tablinks = document.getElementsByClassName("tablinks");
    if (tablinks.length > 0) {
        tablinks[0].click();
    }
    
    // 确保只绑定一次提交事件
    if (!submitHandlerBound) {
        const submitButton = document.getElementById('submit-inspection');
        if (submitButton) {
            // 移除可能已存在的事件监听器
            submitButton.removeEventListener('click', handleInspectionSubmit);
            // 绑定新的事件监听器
            submitButton.addEventListener('click', handleInspectionSubmit);
            submitHandlerBound = true;
            console.log('提交事件绑定成功');
        }
    }
}

/**
 * 处理巡检记录提交
 */
async function handleInspectionSubmit(event) {
    // 阻止默认行为和事件冒泡
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    console.log('提交按钮被点击');
    
    // 获取表单数据
    const inspectorId = document.getElementById('inspector').value;
    const result = document.getElementById('result-select').value;
    const notes = document.getElementById('notes').value;
    
    // 验证当前线缆ID
    if (!currentCableId) {
        alert('请先扫描线缆二维码');
        return;
    }
    
    // 添加防重复提交机制
    const submitButton = document.getElementById('submit-inspection');
    const originalText = submitButton.textContent;
    
    // 禁用按钮，防止重复点击
    submitButton.disabled = true;
    submitButton.textContent = '提交中...';
    
    try {
        console.log('开始提交数据:', { cable_id: currentCableId, inspector_id: inspectorId });
        
        // 提交巡检记录
        const response = await submitInspection({
            cable_id: currentCableId,
            inspector_id: inspectorId,
            result: result,
            notes: notes
        });
        
        console.log('提交响应:', response);
        
        // 处理响应
        if (response.error) {
            alert('提交失败: ' + response.error);
        } else {
            alert('巡检记录提交成功');
            // 刷新数据
            const data = await fetchCableData(currentCableId);
            if (data) {
                updateCableDisplay(data);
            }
            
            // 清空表单
            document.getElementById('notes').value = '';
        }
    } catch (error) {
        console.error('提交错误:', error);
        alert('提交过程中发生错误: ' + error.message);
    } finally {
        // 恢复按钮状态（延迟2秒防止快速重复点击）
        setTimeout(() => {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }, 2000);
    }
}

/**
 * 更新线缆数据显示
 * @param {Object} data - 线缆数据
 */
function updateCableDisplay(data) {
    // 更新各个部分的数据显示
    displayBasicInfo(data.cable_info);
    displayProcessData(data.processes);
    displayInspectionData(data.inspections);
    displayInventoryData(data.inventory);
}

/**
 * 加载线缆数据
 */
async function loadCableData() {
    // 从URL中获取线缆ID
    const pathSegments = window.location.pathname.split('/');
    const cableId = pathSegments[pathSegments.length - 1];
    
    if (cableId) {
        currentCableId = cableId;
        // 获取并显示线缆数据
        const data = await fetchCableData(cableId);
        if (data) {
            updateCableDisplay(data);
        }
    }
}

// 页面加载完成后执行初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化');
    initUI();
    loadCableData();
});

