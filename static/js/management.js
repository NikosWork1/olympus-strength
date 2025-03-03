// static/js/management.js
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the user management page
    const usersTableBody = document.getElementById('users-table-body');
    if (!usersTableBody) return;

    // Setup search and filter functionality
    const searchInput = document.getElementById('search-members');
    const membershipFilter = document.getElementById('filter-membership');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterUsers);
    }
    
    if (membershipFilter) {
        membershipFilter.addEventListener('change', filterUsers);
    }
    
    // Filter users function
    function filterUsers() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const membershipType = membershipFilter ? membershipFilter.value : '';
        const rows = usersTableBody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const name = row.children[1].textContent.toLowerCase();
            const email = row.children[2].textContent.toLowerCase();
            const membership = row.children[4].textContent;
            
            const nameMatch = name.includes(searchTerm);
            const emailMatch = email.includes(searchTerm);
            const membershipMatch = !membershipType || membership === membershipType;
            
            if ((nameMatch || emailMatch) && membershipMatch) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Setup delete user functionality
    const deleteButtons = document.querySelectorAll('.delete-user');
    const confirmDeleteModal = document.getElementById('confirm-delete-modal');
    const deleteMemberIdInput = document.getElementById('delete-member-id');
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    const confirmDeleteBtn = document.getElementById('confirm-delete');
    
    if (confirmDeleteModal) {
        const closeModalBtn = confirmDeleteModal.querySelector('.close-modal');
        
        // Setup close modal functionality
        function closeDeleteModal() {
            confirmDeleteModal.style.display = 'none';
        }
        
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', closeDeleteModal);
        }
        
        if (cancelDeleteBtn) {
            cancelDeleteBtn.addEventListener('click', closeDeleteModal);
        }
        
        // Handle click outside modal to close
        window.addEventListener('click', (event) => {
            if (event.target === confirmDeleteModal) {
                closeDeleteModal();
            }
        });
    }
    
    // Open delete confirmation modal when delete button is clicked
    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (confirmDeleteModal && deleteMemberIdInput) {
                const memberId = button.getAttribute('data-id');
                deleteMemberIdInput.value = memberId;
                confirmDeleteModal.style.display = 'block';
            }
        });
    });
    
    // Handle delete confirmation
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async () => {
            if (!deleteMemberIdInput) return;
            
            const memberId = deleteMemberIdInput.value;
            if (!memberId) return;
            
            // Show loading state
            const originalButtonText = confirmDeleteBtn.textContent;
            confirmDeleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
            confirmDeleteBtn.disabled = true;
            
            try {
                const response = await fetch(`/api/members/${memberId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Remove the user row from the table
                    const userRow = document.querySelector(`tr[data-id="${memberId}"]`);
                    if (userRow) {
                        userRow.style.opacity = '1';
                        userRow.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                        
                        // Fade out animation
                        userRow.style.opacity = '0';
                        userRow.style.transform = 'translateX(20px)';
                        
                        // Remove after animation
                        setTimeout(() => {
                            userRow.remove();
                        }, 300);
                    }
                    
                    showNotification('Member deleted successfully', 'success');
                } else {
                    showNotification(data.detail || 'Failed to delete member', 'error');
                }
            } catch (error) {
                console.error('Error deleting member:', error);
                showNotification('An error occurred while deleting the member', 'error');
            } finally {
                // Close modal and restore button state
                if (confirmDeleteModal) {
                    confirmDeleteModal.style.display = 'none';
                }
                
                confirmDeleteBtn.innerHTML = originalButtonText;
                confirmDeleteBtn.disabled = false;
            }
        });
    }
    
    // Setup edit user functionality (placeholder for future implementation)
    const editButtons = document.querySelectorAll('.edit-user');
    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            const memberId = button.getAttribute('data-id');
            showNotification('Edit functionality will be available soon!', 'info');
        });
    });
});