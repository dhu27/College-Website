// JS for rename and delete actions on My Lists page

document.addEventListener('DOMContentLoaded', function() {
  // Rename list
  document.querySelectorAll('.btn-rename').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const card = btn.closest('.my-list-card');
      const listId = card.dataset.listId;
      const nameSpan = card.querySelector('.my-list-name');
      const oldName = nameSpan.textContent;
      // Create inline input for renaming
      if (card.querySelector('.rename-input')) return;
      const input = document.createElement('input');
      input.type = 'text';
      input.value = oldName;
      input.className = 'rename-input';
      input.style.fontSize = '1.15em';
      input.style.fontWeight = '600';
      input.style.color = 'var(--primary-700)';
      input.style.border = '1px solid var(--primary-300)';
      input.style.borderRadius = '6px';
      input.style.padding = '0.2em 0.5em';
      input.style.marginRight = '0.3em';
      nameSpan.style.display = 'none';
      nameSpan.parentNode.insertBefore(input, nameSpan);
      input.focus();
      input.select();
      // Save on blur or Enter
      function finishRename(save) {
        if (save && input.value && input.value !== oldName) {
          fetch(`/api/lists/${listId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: input.value })
          })
          .then(res => res.json())
          .then(data => {
            if (data.name) {
              nameSpan.textContent = data.name;
            } else {
              alert(data.error || 'Rename failed');
            }
            cleanup();
          });
        } else {
          cleanup();
        }
      }
      function cleanup() {
        input.remove();
        nameSpan.style.display = '';
      }
      input.addEventListener('blur', function() { finishRename(true); });
      input.addEventListener('keydown', function(ev) {
        if (ev.key === 'Enter') { finishRename(true); }
        if (ev.key === 'Escape') { finishRename(false); }
      });
    });
  });

  // Custom delete confirmation modal
  function showDeleteModal(card, listId, onConfirm) {
    // Remove any existing modal
    document.querySelectorAll('.delete-modal').forEach(m => m.remove());
    const modal = document.createElement('div');
    modal.className = 'delete-modal';
    modal.innerHTML = `
      <div class="delete-modal-backdrop"></div>
      <div class="delete-modal-content">
        <div class="delete-modal-title">Delete List</div>
        <div class="delete-modal-message">Are you sure you want to delete this list?</div>
        <div class="delete-modal-actions">
          <button class="btn btn-secondary delete-cancel">Cancel</button>
          <button class="btn btn-primary delete-confirm">Delete</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.querySelector('.delete-cancel').onclick = function() {
      modal.remove();
    };
    modal.querySelector('.delete-confirm').onclick = function() {
      modal.remove();
      onConfirm();
    };
  }

  // Delete list
  document.querySelectorAll('.btn-delete').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const card = btn.closest('.my-list-card');
      const listId = card.dataset.listId;
      showDeleteModal(card, listId, function() {
        fetch(`/api/lists/${listId}`, {
          method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            card.remove();
          } else {
            alert(data.error || 'Delete failed');
          }
        });
      });
    });
  });
});
