document.addEventListener('DOMContentLoaded', () => {
    const telegram = window.Telegram.WebApp;
    const initData = telegram.initData;
    const form = document.querySelector('form');
    if (initData && form) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'init_data';
        input.value = initData;
        form.appendChild(input);
    }
    const containers = document.querySelectorAll('.image_container');
    const counter = document.getElementById('selected-count');

    function updateCounter() {
        counter.textContent = document.querySelectorAll('.image_container input[type="checkbox"]:checked').length;
    }

    containers.forEach(container => {
        container.addEventListener('click', () => {
            const checkbox = container.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
            container.classList.toggle('selected', checkbox.checked);
            updateCounter();
        });
    });

    updateCounter();


    // Categories
    const menuButton = document.getElementById('menu-button');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    // Открытие/закрытие сайдбара
    menuButton.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
    });

    // Закрытие при клике на оверлее
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.style.display = 'none';
    });
});