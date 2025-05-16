document.addEventListener('DOMContentLoaded', () => {
    const telegram = window.Telegram.WebApp;
    const user = telegram.initDataUnsafe?.user;

    if (user) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'telegram_user_id';
        input.value = user.id;
        document.querySelector('form').appendChild(input);
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
});