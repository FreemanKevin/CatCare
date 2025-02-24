document.addEventListener('DOMContentLoaded', () => {
    fetchRecords();
    document.getElementById('weightForm').addEventListener('submit', addWeight);

    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });
    tabs[0].classList.add('active');
    document.getElementById('weight').classList.add('active');

    // 语言切换
    const languageSwitch = document.getElementById('languageSwitch');
    if (languageSwitch) {
        languageSwitch.addEventListener('click', () => {
            const currentLocale = document.querySelector('#languageSwitch span').textContent === '中文' ? 'en' : 'zh';
            fetch(`/switch-language/${currentLocale}`)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    window.location.reload();
                })
                .catch(error => console.error('Error switching language:', error));
        });
    } else {
        console.error('Language switch button not found');
    }

    // 主题切换
    const themeSwitch = document.getElementById('themeSwitch');
    if (themeSwitch) {
        themeSwitch.addEventListener('click', () => {
            const currentTheme = document.querySelector('#themeSwitch span').textContent === '明' ? 'dark' : 'light';
            fetch(`/switch-theme/${currentTheme}`)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    window.location.reload();
                })
                .catch(error => console.error('Error switching theme:', error));
        });
    } else {
        console.error('Theme switch button not found');
    }
});

function fetchRecords() {
    fetch('/api/records')
        .then(response => response.json())
        .then(data => {
            const weightList = document.getElementById('weightList');
            weightList.innerHTML = '';
            data.weight.forEach(record => {
                const div = document.createElement('div');
                div.className = 'bg-gray-50 p-4 rounded-lg shadow';
                div.innerHTML = `
                    <p class="text-gray-800 font-medium">${record.date} - ${record.weight}kg</p>
                    ${record.image ? `<img src="/cat_data/${record.image.split('/').pop()}" class="card-img mt-2">` : '<p class="text-gray-500 text-sm">无图片</p>'}
                `;
                weightList.appendChild(div);
            });
        });
}

function addWeight(event) {
    event.preventDefault();
    const form = document.getElementById('weightForm');
    const formData = new FormData(form);
    fetch('/api/add_weight', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        alert(data.message);
        form.reset();
        document.querySelector('input[name="date"]').value = new Date().toISOString().split('T')[0];
        fetchRecords();
    })
    .catch(error => alert('错误: ' + error.message));
}