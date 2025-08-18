// Handles selection/removal of colleges from a list

const removeBtn = document.getElementById('remove-from-list-btn');
const confirmRemoveBtn = document.getElementById('confirm-remove-btn');
const cancelRemoveBtn = document.getElementById('cancel-remove-btn');
const checkboxes = document.querySelectorAll('.remove-checkbox');


const cardLinks = document.querySelectorAll('.list-college-card-link');
let removeMode = false;

removeBtn.addEventListener('click', () => {
    checkboxes.forEach(cb => {
        cb.style.display = 'inline-block';
    });
    confirmRemoveBtn.style.display = 'inline-block';
    cancelRemoveBtn.style.display = 'inline-block';
    removeBtn.style.display = 'none';
    removeMode = true;
    cardLinks.forEach(link => {
        link.addEventListener('click', preventLink, true);
        link.classList.add('disabled-link');
    });
});

function preventLink(e) {
    if (removeMode) {
        // Only prevent if the click is not on a checkbox
        if (!e.target.classList.contains('remove-checkbox')) {
            e.preventDefault();
            e.stopPropagation();
        }
    }
}


cancelRemoveBtn.addEventListener('click', () => {
    checkboxes.forEach(cb => {
        cb.checked = false;
        cb.style.display = 'none';
    });
    confirmRemoveBtn.style.display = 'none';
    cancelRemoveBtn.style.display = 'none';
    removeBtn.style.display = 'inline-block';
    removeMode = false;
    cardLinks.forEach(link => {
        link.removeEventListener('click', preventLink, true);
        link.classList.remove('disabled-link');
    });
});

const form = document.getElementById('remove-colleges-form');
form.addEventListener('submit', () => {
    checkboxes.forEach(cb => {
        cb.style.display = 'none';
    });
    confirmRemoveBtn.style.display = 'none';
    cancelRemoveBtn.style.display = 'none';
    removeBtn.style.display = 'inline-block';
});
