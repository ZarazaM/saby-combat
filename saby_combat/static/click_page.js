document.addEventListener("DOMContentLoaded", function() {
    // Получаем элементы
    const clickButton = document.getElementById('click-button');
    const moneyCounter = document.getElementById('money-count');
    let clickCount = 0;

    // Загрузка количества монет из localStorage
    if (localStorage.getItem('clickCount')) {
        clickCount = parseInt(localStorage.getItem('clickCount'), 10);
        moneyCounter.textContent = parseInt(moneyCounter.textContent) + clickCount * 1;
    }

    // Обработка на клик, чтобы прибавлялись монеты
    clickButton.addEventListener('click', function() {
        clickCount += 1;
        moneyCounter.textContent = parseInt(moneyCounter.textContent) + 1 * 1;
        localStorage.setItem('clickCount', clickCount);
    });

    // Функция для отправки данных на сервер
    function submitClicks() {
        const clicksToSubmit = parseInt(localStorage.getItem('clickCount'), 10) || 0;

        if (clicksToSubmit > 0) {
            fetch('/submit_clicks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ clicks: clicksToSubmit, money: moneyCounter.textContent}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    localStorage.removeItem('clickCount');
                    clickCount = 0;
                } else {
                    console.error('Error:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    }

    // Отправка данных каждые 30 секунд
    setInterval(submitClicks, 30000);
});
