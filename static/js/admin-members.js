// Add these functions to a new file: static/js/admin-members.js

document.addEventListener('DOMContentLoaded', () => {
    // Load members list when the Members menu item is clicked
    document.querySelector('#members-menu-item').addEventListener('click', loadMembersManagement);
    
    // Setup member actions if we're on the members page
    if (document.querySelector('#members-container')) {
        setupMemberActions();
    }
});

// Function to load the members management UI
function loadMembersManagement() {
    const contentArea = document.querySelector('#admin-content-area');
    
    // Show loading state
    contentArea.innerHTML = '<div class="loading">Loading members...</div>';
    
    // Fetch members data from API
    fetch('/api/members')
        .then(response => response.json())
        .then(members => {
            // Generate members table UI
            let membersHTML = `
                <div id="members-container">
                    <div class="admin-header">
                        <h2>Members Management</h2>
                        <button id="add-member-btn" class="btn">Add New Member</button>
                    </div>
                    
                    <div class="search-filter">
                        <input type="text" id="search-members" placeholder="Search members...">
                        <select id="membership-filter">
                            <option value="">All Membership Types</option>
                            <option value="Bronze">Bronze</option>
                            <option value="Silver">Silver</option>
                            <option value="Gold">Gold</option>
                        </select>
                    </div>
                    
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Membership</th>
                                <th>Join Date</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            members.forEach(member => {
                membersHTML += `
                    <tr data-id="${member.id}">
                        <td>${member.id}</td>
                        <td>${member.name}</td>
                        <td>${member.email}</td>
                        <td>${member.membership_type}</td>
                        <td>${new Date(member.join_date).toLocaleDateString()}</td>
                        <td>
                            <span class="status-badge ${member.is_active ? 'active' : 'inactive'}">
                                ${member.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </td>
                        <td>
                            <button class="action-btn edit-member" data-id="${member.id}">✏️</button>
                            <button class="action-btn delete-member" data-id="${member.id}">🗑️</button>
                        </td>
                    </tr>
                `;
            });
            
            membersHTML += `
                        </tbody>
                    </table>
                </div>
                
                <!-- Member Form Modal -->
                <div id="member-modal" class="modal">
                    <div class="modal-content">
                        <span class="close-modal">&times;</span>
                        <h2 id="modal-title">Add New Member</h2>
                        
                        <form id="member-form">
                            <input type="hidden" id="member-id">
                            
                            <div class="form-group">
                                <label for="name">Full Name</label>
                                <input type="text" id="name" name="name" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="email">Email</label>
                                <input type="email" id="email" name="email" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="phone">Phone</label>
                                <input type="text" id="phone" name="phone">
                            </div>
                            
                            <div class="form-group">
                                <label for="membership_type">Membership Type</label>
                                <select id="membership_type" name="membership_type" required>
                                    <option value="Bronze">Bronze</option>
                                    <option value="Silver">Silver</option>
                                    <option value="Gold">Gold</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="password">Password</label>
                                <input type="password" id="password" name="password">
                                <small>(Leave blank to keep current password when editing)</small>
                            </div>
                            
                            <div class="form-group">
                                <label>Status</label>
                                <div class="radio-group">
                                    <label>
                                        <input type="radio" name="is_active" value="true" checked> Active
                                    </label>
                                    <label>
                                        <input type="radio" name="is_active" value="false"> Inactive
                                    </label>
                                </div>
                            </div>
                            
                            <div class="form-actions">
                                <button type="button" id="cancel-member">Cancel</button>
                                <button type="submit" id="save-member">Save Member</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- Delete Confirmation Modal -->
                <div id="delete-confirm-modal" class="modal">
                    <div class="modal-content">
                        <span class="close-modal">&times;</span>
                        <h2>Confirm Deletion</h2>
                        <p>Are you sure you want to delete this member? This action cannot be undone.</p>
                        <input type="hidden" id="delete-member-id">
                        <div class="modal-actions">
                            <button id="cancel-delete">Cancel</button>
                            <button id="confirm-delete">Delete Member</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Update the content area
            contentArea.innerHTML = membersHTML;
            
            // Setup event handlers for the member actions
            setupMemberActions();
        })
        .catch(error => {
            contentArea.innerHTML = `<div class="error">Error loading members: ${error.message}</div>`;
        });
}

// Function to setup all member action event handlers
function setupMemberActions() {
    // Add new member button
    const addMemberBtn = document.getElementById('add-member-btn');
    if (addMemberBtn) {
        addMemberBtn.addEventListener('click', () => {
            openMemberModal();
        });
    }
    
    // Edit member buttons
    const editButtons = document.querySelectorAll('.edit-member');
    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            const memberId = button.getAttribute('data-id');
            fetchMemberDetails(memberId);
        });
    });
    
    // Delete member buttons
    const deleteButtons = document.querySelectorAll('.delete-member');
    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const memberId = button.getAttribute('data-id');
            openDeleteModal(memberId);
        });
    });
    
    // Member form submission
    const memberForm = document.getElementById('member-form');
    if (memberForm) {
        memberForm.addEventListener('submit', saveMember);
    }
    
    // Cancel buttons
    const cancelMemberBtn = document.getElementById('cancel-member');
    if (cancelMemberBtn) {
        cancelMemberBtn.addEventListener('click', closeModal);
    }
    
    // Modal close buttons
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', closeModal);
    });
    
    // Delete confirmation
    const confirmDeleteBtn = document.getElementById('confirm-delete');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', deleteMember);
    }
    
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeModal);
    }
    
    // Search functionality
    const searchInput = document.getElementById('search-members');
    if (searchInput) {
        searchInput.addEventListener('input', filterMembers);
    }
    
    // Membership filter
    const membershipFilter = document.getElementById('membership-filter');
    if (membershipFilter) {
        membershipFilter.addEventListener('change', filterMembers);
    }
}

// Function to filter members
function filterMembers() {
    const searchTerm = document.getElementById('search-members').value.toLowerCase();
    const membershipType = document.getElementById('membership-filter').value;
    const rows = document.querySelectorAll('#members-container table tbody tr');
    
    rows.forEach(row => {
        const name = row.children[1].textContent.toLowerCase();
        const email = row.children[2].textContent.toLowerCase();
        const membership = row.children[3].textContent;
        
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

// Function to open the member modal for adding a new member
function openMemberModal(memberId = null) {
    const modal = document.getElementById('member-modal');
    const modalTitle = document.getElementById('modal-title');
    const form = document.getElementById('member-form');
    const memberIdInput = document.getElementById('member-id');
    
    // Reset the form
    form.reset();
    
    // Set the modal title and member ID based on whether we're adding or editing
    if (memberId) {
        modalTitle.textContent = 'Edit Member';
        memberIdInput.value = memberId;
    } else {
        modalTitle.textContent = 'Add New Member';
        memberIdInput.value = '';
    }
    
    // Show the modal
    modal.style.display = 'block';
}

// Function to fetch member details for editing
function fetchMemberDetails(memberId) {
    fetch(`/api/members/${memberId}`)
        .then(response => response.json())
        .then(member => {
            // Open the modal
            openMemberModal(memberId);
            
            // Fill the form with member details
            document.getElementById('name').value = member.name;
            document.getElementById('email').value = member.email;
            document.getElementById('phone').value = member.phone || '';
            document.getElementById('membership_type').value = member.membership_type;
            
            // Set active status
            const activeRadio = document.querySelector('input[name="is_active"][value="true"]');
            const inactiveRadio = document.querySelector('input[name="is_active"][value="false"]');
            
            if (member.is_active) {
                activeRadio.checked = true;
            } else {
                inactiveRadio.checked = true;
            }
        })
        .catch(error => {
            showNotification(`Error fetching member details: ${error.message}`, 'error');
        });
}

// Function to save a member (create or update)
function saveMember(e) {
    e.preventDefault();
    
    const memberId = document.getElementById('member-id').value;
    const isEditing = !!memberId;
    
    // Get form data
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        membership_type: document.getElementById('membership_type').value,
        is_active: document.querySelector('input[name="is_active"]:checked').value === 'true'
    };
    
    // Add password only if it's not empty
    const password = document.getElementById('password').value;
    if (password) {
        formData.password = password;
    }
    
    // API endpoint and method based on whether we're creating or updating
    const url = isEditing ? `/api/members/${memberId}` : '/api/members';
    const method = isEditing ? 'PUT' : 'POST';
    
    // Make the API request
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Close the modal
        closeModal();
        
        // Show success message
        showNotification(`Member ${isEditing ? 'updated' : 'created'} successfully!`, 'success');
        
        // Reload the members list
        loadMembersManagement();
    })
    .catch(error => {
        showNotification(`Error saving member: ${error.message}`, 'error');
    });
}

// Function to open the delete confirmation modal
function openDeleteModal(memberId) {
    const modal = document.getElementById('delete-confirm-modal');
    const memberIdInput = document.getElementById('delete-member-id');
    
    // Set the member ID to delete
    memberIdInput.value = memberId;
    
    // Show the modal
    modal.style.display = 'block';
}

// Function to delete a member
function deleteMember() {
    const memberId = document.getElementById('delete-member-id').value;
    
    // Make the API request to delete the member
    fetch(`/api/members/${memberId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Close the modal
        closeModal();
        
        // Show success message
        showNotification('Member deleted successfully!', 'success');
        
        // Remove the row from the table or reload the members list
        const row = document.querySelector(`tr[data-id="${memberId}"]`);
        if (row) {
            row.remove();
        } else {
            loadMembersManagement();
        }
    })
    .catch(error => {
        showNotification(`Error deleting member: ${error.message}`, 'error');
    });
}

// Function to close any open modal
function closeModal() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
}
