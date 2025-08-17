// JS for Add to List dropdown functionality with animated pop-out

document.addEventListener('DOMContentLoaded', function() {
  // Show dropdown on button click
  document.querySelectorAll('.add-to-list-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      const collegeId = btn.getAttribute('data-college-id');
      const dropdown = document.querySelector('.list-dropdown[data-college-id="' + collegeId + '"]');
      // Hide all dropdowns first
      document.querySelectorAll('.list-dropdown').forEach(d => {
        d.classList.remove('show');
        d.style.position = '';
        d.style.top = '';
        d.style.left = '';
        d.style.width = '';
      });
      // Position dropdown using fixed so it escapes parent containers
  dropdown.classList.add('show');
  dropdown.style.position = '';
  dropdown.style.top = '';
  dropdown.style.left = '';
  dropdown.style.width = '';
      // Fetch lists if not already loaded
      if (!dropdown.dataset.loaded) {
        fetch('/api/lists')
          .then(res => res.json())
          .then(lists => {
            const listsDiv = dropdown.querySelector('.user-lists');
            listsDiv.innerHTML = '';
            lists.forEach(list => {
              const label = document.createElement('label');
              label.innerHTML = `<input type="checkbox" name="list_ids" value="${list.id}"> ${list.name}`;
              listsDiv.appendChild(label);
            });
            dropdown.dataset.loaded = 'true';
          });
      }
    });
  });

  // Hide dropdown when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.classList.contains('add-to-list-btn') && !e.target.closest('.list-dropdown')) {
      document.querySelectorAll('.list-dropdown').forEach(d => {
        d.classList.remove('show');
      });
    }
  });

  // Handle create new list
  document.querySelectorAll('.create-list-btn').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const dropdown = btn.closest('.list-dropdown');
      const newListName = dropdown.querySelector('.new-list-name').value.trim();
      if (!newListName) return;
      fetch('/api/lists', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newListName })
      })
      .then(res => res.json())
      .then(list => {
        // Add new list to checkboxes
        const listsDiv = dropdown.querySelector('.user-lists');
        const label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" name="list_ids" value="${list.id}" checked> ${list.name}`;
        listsDiv.appendChild(label);
        dropdown.querySelector('.new-list-name').value = '';
      });
    });
  });

  // Handle add college to selected lists
  document.querySelectorAll('.add-to-list-form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const dropdown = form.closest('.list-dropdown');
      const collegeId = dropdown.getAttribute('data-college-id');
      const checked = Array.from(form.querySelectorAll('input[name="list_ids"]:checked'));
      checked.forEach(function(cb) {
        fetch(`/api/lists/${cb.value}/colleges`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ college_id: collegeId })
        })
        .then(res => res.json())
        .then(resp => {
          // Optionally show success/error message
        });
      });
      dropdown.classList.remove('show');
    });
  });
});
