const API_BASE = '/api';

// State
let devices = [];
let currentSection = 'dashboard';

// Navigation
function showSection(id) {
    document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
    document.getElementById(`section-${id}`).classList.remove('hidden');

    document.querySelectorAll('nav li').forEach(l => l.classList.remove('active'));
    document.getElementById(`nav-${id}`).classList.add('active');

    currentSection = id;
    onSectionLoaded(id);
}

function onSectionLoaded(id) {
    switch (id) {
        case 'dashboard': getServerInfo(); break;
        case 'devices': refreshDevices(); break;
        case 'commands': loadCommands(); break;
        case 'notifications': loadNotifications(); break;
        case 'advanced': populateDeviceSelects(); break;
    }
}

// API Helpers
async function apiRequest(path, method = 'GET', body = null) {
    const options = {
        method,
        headers: {}
    };
    if (body) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(API_BASE + path, options);
        const data = await response.json();
        if (!data.success) throw new Error(data.message || 'API Error');
        return data;
    } catch (err) {
        console.error(err);
        alert('Error: ' + err.message);
        throw err;
    }
}

// Section: Dashboard
async function getServerInfo() {
    const data = await apiRequest('/');
    const output = document.getElementById('server-info');
    output.innerHTML = `
    <p><strong>Server:</strong> ${data.server}</p>
    <p><strong>Device Name:</strong> ${data.device}</p>
    <p><strong>Identifier:</strong> <code style="font-size: 12px;">${data.identifier}</code></p>
`;
}

async function broadcastIdentity() {
    await apiRequest('/', 'PUT');
    alert('Broadcast sent!');
}

async function getVersion() {
    const data = await apiRequest('/version');
    document.getElementById('version-output').textContent = JSON.stringify(data, null, 2);
}

// Section: Devices
async function refreshDevices() {
    const data = await apiRequest('/device');
    devices = data.devices;
    renderDevices();
    populateDeviceSelects();
}

function renderDevices() {
    const container = document.getElementById('device-list');
    container.innerHTML = '';

    devices.forEach(dev => {
        const card = document.createElement('div');
        card.className = 'device-card';

        const statusClass = dev.reachable ? 'status-online' : 'status-offline';
        const statusText = dev.reachable ? 'Online' : 'Offline';
        const pairAction = dev.trusted ?
            `<button class="danger" onclick="unpairDevice('${dev.identifier}')">Unpair</button>` :
            `<button onclick="pairDevice('${dev.identifier}')">Pair Device</button>`;

        card.innerHTML = `
        <div class="device-header">
            <strong>${dev.name}</strong>
            <span class="status-badge ${statusClass}">${statusText}</span>
        </div>
        <div style="font-size: 13px; color: var(--text-dim);">
            Type: ${dev.type}<br>
            ID: ${dev.identifier}
        </div>
        <div class="flex-row">
            <button class="secondary" onclick="pingDevice('${dev.identifier}')" ${!dev.reachable ? 'disabled' : ''}>Ping</button>
            <button class="secondary" onclick="ringDevice('${dev.identifier}')" ${!dev.reachable ? 'disabled' : ''}>Ring</button>
            ${pairAction}
        </div>
    `;
        container.appendChild(card);
    });
}

async function pairDevice(id) {
    await apiRequest(`/pair/${id}`, 'POST');
    alert('Pairing request sent to device.');
    refreshDevices();
}

async function unpairDevice(id) {
    if (!confirm('Are you sure you want to unpair this device?')) return;
    await apiRequest(`/pair/${id}`, 'DELETE');
    refreshDevices();
}

async function pingDevice(id) {
    await apiRequest(`/ping/${id}`, 'POST');
}

async function ringDevice(id) {
    await apiRequest(`/ring/${id}`, 'POST');
}

// Section: Commands
async function loadCommands() {
    const data = await apiRequest('/command');
    const tbody = document.querySelector('#local-commands-table tbody');
    tbody.innerHTML = '';

    data.commands.forEach(cmd => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td>${cmd.device}</td>
        <td>${cmd.name}</td>
        <td><code>${cmd.command}</code></td>
        <td>
            <button class="secondary" onclick="openEditCommandModal('${cmd.identifier}', '${cmd.key}', '${cmd.name}', '${cmd.command}')">Edit</button>
            <button class="danger" onclick="deleteCommand('${cmd.identifier}', '${cmd.key}')">Delete</button>
        </td>
    `;
        tbody.appendChild(tr);
    });
    populateDeviceSelects();
}

async function loadRemoteCommands() {
    const deviceId = document.getElementById('remote-cmd-device').value;
    const select = document.getElementById('remote-cmd-list');
    select.innerHTML = '<option value="">-- Select Command --</option>';

    if (!deviceId) return;

    const dev = devices.find(d => d.identifier === deviceId);
    if (dev && dev.commands) {
        Object.entries(dev.commands).forEach(([key, cmd]) => {
            const opt = document.createElement('option');
            opt.value = key;
            opt.textContent = cmd.name;
            select.appendChild(opt);
        });
    }
}

async function executeRemoteCommand() {
    const deviceId = document.getElementById('remote-cmd-device').value;
    const key = document.getElementById('remote-cmd-list').value;
    if (!deviceId || !key) return alert('Select device and command');

    await apiRequest(`/command/${deviceId}/${key}`, 'PATCH');
    alert('Command execution request sent.');
}

// Section: Notifications
async function loadNotifications() {
    const data = await apiRequest('/notification');
    const tbody = document.querySelector('#notifications-table tbody');
    tbody.innerHTML = '';

    data.notifications.forEach(n => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
        <td>${n.device}</td>
        <td>${n.title}</td>
        <td>${n.text}</td>
        <td><code>${n.reference}</code></td>
        <td>
            <button class="danger" onclick="cancelNotification('${n.identifier}', '${n.reference}')">Cancel</button>
        </td>
    `;
        tbody.appendChild(tr);
    });
    populateDeviceSelects();
}

async function sendNotification() {
    const device = document.getElementById('notif-device').value;
    const title = document.getElementById('notif-title').value;
    const app = document.getElementById('notif-app').value;
    const text = document.getElementById('notif-text').value;
    const icon = document.getElementById('notif-icon').value;

    if (!device || !text || !title || !app) return alert('Please fill required fields');

    await apiRequest(`/notification/${device}`, 'POST', {
        title, text, application: app, icon: icon || undefined
    });
    alert('Notification sent!');
    loadNotifications();
}

async function cancelNotification(deviceId, reference) {
    await apiRequest(`/notification/${deviceId}/${reference}`, 'DELETE');
    loadNotifications();
}

// Section: Advanced
async function updateSharePath() {
    const device = document.getElementById('share-device').value;
    const path = document.getElementById('share-path').value;
    if (!device) return alert('Select a device');

    await apiRequest(`/share/${device}`, 'PATCH', { path: path || null });
    alert('Share configuration updated.');
}

async function sendCustomPacket() {
    const device = document.getElementById('custom-device').value;
    const jsonStr = document.getElementById('custom-json').value;
    if (!device || !jsonStr) return alert('Fill required fields');

    try {
        const body = JSON.parse(jsonStr);
        await apiRequest(`/custom/${device}`, 'POST', body);
        alert('Custom packet sent!');
    } catch (e) {
        alert('Invalid JSON: ' + e.message);
    }
}

// Modals & Selects
function populateDeviceSelects() {
    const ids = ['remote-cmd-device', 'notif-device', 'share-device', 'custom-device', 'modal-cmd-device'];
    ids.forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        const currentVal = select.value;
        select.innerHTML = '<option value="">-- Select Device --</option>';
        devices.forEach(dev => {
            const opt = document.createElement('option');
            opt.value = dev.identifier;
            opt.textContent = `${dev.name} (${dev.reachable ? 'Online' : 'Offline'})`;
            select.appendChild(opt);
        });
        select.value = currentVal;
    });
}

function openAddCommandModal() {
    document.getElementById('modal-title').textContent = 'Add Local Command';
    document.getElementById('modal-cmd-key').value = '';
    document.getElementById('modal-cmd-name').value = '';
    document.getElementById('modal-cmd-exec').value = '';
    document.getElementById('modal-cmd-device').disabled = false;
    document.getElementById('modal-container').classList.remove('hidden');
}

function openEditCommandModal(deviceId, key, name, exec) {
    document.getElementById('modal-title').textContent = 'Edit Local Command';
    document.getElementById('modal-cmd-key').value = key;
    document.getElementById('modal-cmd-name').value = name;
    document.getElementById('modal-cmd-exec').value = exec;
    document.getElementById('modal-cmd-device').value = deviceId;
    document.getElementById('modal-cmd-device').disabled = true;
    document.getElementById('modal-container').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-container').classList.add('hidden');
}

async function saveCommand() {
    const deviceId = document.getElementById('modal-cmd-device').value;
    const key = document.getElementById('modal-cmd-key').value;
    const name = document.getElementById('modal-cmd-name').value;
    const command = document.getElementById('modal-cmd-exec').value;

    if (!deviceId || !name || !command) return alert('Fill all fields');

    if (key) {
        // Update
        await apiRequest(`/command/${deviceId}/${key}`, 'PUT', { name, command });
    } else {
        // Create
        await apiRequest(`/command/${deviceId}`, 'POST', { name, command });
    }

    closeModal();
    loadCommands();
}

async function deleteCommand(deviceId, key) {
    if (!confirm('Delete this command?')) return;
    await apiRequest(`/command/${deviceId}/${key}`, 'DELETE');
    loadCommands();
}

// Init
window.onload = () => {
    getServerInfo();
    refreshDevices();
};
