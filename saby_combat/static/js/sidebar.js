document.addEventListener("DOMContentLoaded", function() {
    const path = window.location.pathname;

    // Удаляем класс active у всех элементов
    document.querySelectorAll('.container-for-element-menu').forEach(el => el.classList.remove('active'));

    // Находим элемент, соответствующий текущему пути
    const activeElement = document.querySelector(`a[href="${path}"]`).closest('.container-for-element-menu');

    // Добавляем класс active только к найденному элементу
    if (activeElement) {
        activeElement.classList.add('active');
    }
});

