document.addEventListener("DOMContentLoaded", function() {
    // Получаем элементы
    const clickButton = document.getElementById('click-button');
    const moneyCounter = document.getElementById('money-count');
    let clickCount = 0; //Количество кликов за 30 секунд
    let coinsPerSecondAccumulated = parseInt(localStorage.getItem('coinsPerSecondAccumulated')) || 0;
    const coinsPerClick = ;
    const coinsPerSecond = ;

    // Загрузка количества монет из localStorage при открытии страницы
    if (localStorage.getItem('clickCount')) {
        clickCount = parseInt(localStorage.getItem('clickCount'), 10);
        moneyCounter.textContent = parseInt(moneyCounter.textContent) + clickCount * coinsPerClick;

        if (localStorage.getItem('coinsPerSecondAccumulated')) {
        moneyCounter.textContent = parseInt(moneyCounter.textContent) + coinsPerSecondAccumulated;
        }
    }

    // Обработка на клик, чтобы прибавлялись монеты
    clickButton.addEventListener('click', function() {
        clickCount += 1;
        moneyCounter.textContent = parseInt(moneyCounter.textContent) + coinsPerClick;
        localStorage.setItem('clickCount', clickCount);
    });

    // Функция для отправки данных на сервер
    function submitClicks() {
        const clicksToSubmit = parseInt(localStorage.getItem('clickCount'), 10) || 0;
        const coinsToSubmit = parseInt(localStorage.getItem('coinsPerSecondAccumulated'), 10) || 0;

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
        moneyCounter.textContent = parseInt(moneyCounter.textContent) + coinsPerSecond;
        localStorage.setItem('coinsPerSecondAccumulated', coinsPerSecondAccumulated);
    }

    // Обновляем количество монет каждую секунду
    setInterval(accumulateCoinsPerSecond, 1000);
});
