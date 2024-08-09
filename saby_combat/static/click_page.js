document.addEventListener("DOMContentLoaded", function() {
    // Получаем элементы
    const clickButton = document.getElementById('click-button');
    const moneyCounter = document.getElementById('money-count');
    let clickCount = 0; //Количество кликов за 30 секунд
    let coinsPerSecondAccumulated = parseFloat(localStorage.getItem('coinsPerSecondAccumulated')) || 0;
    const coinsPerClick = parseInt(document.getElementById('coins_per_click').textContent);
    const coinsPerSecond = parseFloat(document.getElementById('coins_per_second').textContent);
    const progressBar = document.getElementById('progress-bar');

    // Загрузка количества монет из localStorage при открытии страницы и прогресса
    if (localStorage.getItem('clickCount')) {
        clickCount = parseInt(localStorage.getItem('clickCount'), 10) || 0;
        moneyCounter.textContent = parseFloat(moneyCounter.textContent) + clickCount * coinsPerClick;
        progressBar.value = parseFloat(moneyCounter.textContent);
    }
    if (localStorage.getItem('coinsPerSecondAccumulated')) {
        moneyCounter.textContent = parseFloat(moneyCounter.textContent) + coinsPerSecondAccumulated;
        progressBar.value = parseFloat(moneyCounter.textContent);
    }

    // Обработка на клик, чтобы прибавлялись монеты
    clickButton.addEventListener('click', function() {
        clickCount += 1;
        moneyCounter.textContent = parseFloat(moneyCounter.textContent) + coinsPerClick;
        progressBar.value = parseFloat(moneyCounter.textContent);
        localStorage.setItem('clickCount', clickCount);
    });

    // Функция для отправки данных на сервер
    function submitClicks() {
        const clicksToSubmit = parseInt(localStorage.getItem('clickCount'), 10) || 0;
        const coinsToSubmit = parseFloat(localStorage.getItem('coinsPerSecondAccumulated'), 10) || 0;

        if (clicksToSubmit > 0 || coinsToSubmit > 0) {
            fetch('/submit_clicks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ clicks: clicksToSubmit, money: moneyCounter.textContent, coinsPerSecondAccumulated: coinsToSubmit}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    localStorage.removeItem('clickCount');
                    localStorage.removeItem('coinsPerSecondAccumulated');
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

    // Функция для накопления монет от coinsPerSecond
    function accumulateCoinsPerSecond() {
        coinsPerSecondAccumulated += coinsPerSecond;
        moneyCounter.textContent = parseFloat(moneyCounter.textContent) + coinsPerSecond;
        progressBar.value = parseFloat(moneyCounter.textContent);
        localStorage.setItem('coinsPerSecondAccumulated', coinsPerSecondAccumulated);
    }

    // Обновляем количество монет каждую секунду
    setInterval(accumulateCoinsPerSecond, 1000);
});
