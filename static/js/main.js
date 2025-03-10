// static/js/main.js
// Common JavaScript functions used across the site

// Helper function to make API requests
async function apiRequest(url, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
        showNotification(`Error: ${error.message}`, 'error');
        return null;
    }
}

// Simple notification function
function showNotification(message, type = 'success') {
    // Check if notification container exists, if not create it
    let notificationContainer = document.querySelector('.notification-container');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'notification-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = () => notification.remove();
    notification.appendChild(closeBtn);
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Setup mobile navigation
function setupMobileNav() {
    const mobileToggle = document.querySelector('.mobile-toggle');
    const nav = document.querySelector('.nav');
    
    if (mobileToggle && nav) {
        mobileToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }
}

// Setup dropdown menus - uses click instead of hover
function setupDropdowns() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Close all other dropdowns first
            document.querySelectorAll('.dropdown').forEach(dropdown => {
                if (dropdown !== this.parentElement) {
                    dropdown.classList.remove('active');
                    const icon = dropdown.querySelector('.dropdown-icon');
                    if (icon) {
                        icon.textContent = '▼';
                    }
                }
            });
            
            // Toggle current dropdown
            const dropdown = this.parentElement;
            dropdown.classList.toggle('active');
            
            // Update the dropdown icon
            const icon = this.querySelector('.dropdown-icon');
            if (icon) {
                icon.textContent = dropdown.classList.contains('active') ? '▲' : '▼';
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-toggle')) {
            document.querySelectorAll('.dropdown').forEach(dropdown => {
                dropdown.classList.remove('active');
                const icon = dropdown.querySelector('.dropdown-icon');
                if (icon) {
                    icon.textContent = '▼';
                }
            });
        }
    });
}

// Setup smooth scrolling for anchor links
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            
            // Skip if it's just "#" or if it's a button with other actions
            if (targetId === '#' || this.classList.contains('btn-sm') || this.classList.contains('dropdown-toggle')) return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Setup form validations
function setupFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredInputs = form.querySelectorAll('[required]');
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('error');
                    
                    // Create error message if not exists
                    let errorMsg = input.parentNode.querySelector('.error-text');
                    if (!errorMsg) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-text';
                        errorMsg.textContent = 'This field is required';
                        input.parentNode.appendChild(errorMsg);
                    }
                } else {
                    input.classList.remove('error');
                    const errorMsg = input.parentNode.querySelector('.error-text');
                    if (errorMsg) errorMsg.remove();
                }
            });
            
            // Check password matching for signup form
            const password = form.querySelector('#password');
            const confirmPassword = form.querySelector('#confirm_password');
            
            if (password && confirmPassword && password.value && confirmPassword.value) {
                if (password.value !== confirmPassword.value) {
                    isValid = false;
                    confirmPassword.classList.add('error');
                    
                    let errorMsg = confirmPassword.parentNode.querySelector('.error-text');
                    if (!errorMsg) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-text';
                        errorMsg.textContent = 'Passwords do not match';
                        confirmPassword.parentNode.appendChild(errorMsg);
                    } else {
                        errorMsg.textContent = 'Passwords do not match';
                    }
                }
            }
            
            // If form is invalid, prevent submission
            if (!isValid) {
                e.preventDefault();
                showNotification('Please correct the errors in the form', 'error');
            }
        });
    });
}

// Setup modals
function setupModals() {
    // Get all modal triggers and modals
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modals = document.querySelectorAll('.modal');
    
    // Setup modal open triggers
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            
            if (modal) {
                modal.style.display = 'block';
            }
        });
    });
    
    // Setup close buttons
    document.querySelectorAll('.close-modal').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Close modal when clicking outside content
    window.addEventListener('click', function(event) {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// General utility function for booking classes or handling other button actions
function setupActionButtons() {
    // Book class button functionality
    document.querySelectorAll('.btn').forEach(button => {
        if (button.textContent.includes('Book Class')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                showNotification('Class booking functionality will be available soon!', 'info');
            });
        }
    });
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    // Setup mobile navigation
    setupMobileNav();
    
    // Setup dropdown menus
    setupDropdowns();
    
    // Setup smooth scrolling
    setupSmoothScroll();
    
    // Setup form validations
    setupFormValidations();
    
    // Setup modals
    setupModals();
    
    // Setup action buttons
    setupActionButtons();
});
