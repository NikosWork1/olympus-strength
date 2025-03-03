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

// Create and initialize modals if they don't exist
function createModals() {
    // This function is now unnecessary since we have the modals in the HTML
    // We're keeping it for compatibility with existing code that might call it
    console.log("Modals already exist in HTML");
}

// Modal functionality
function setupModals() {
    // Login button functionality
    const loginBtn = document.querySelector('#login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const loginModal = document.getElementById('login-modal');
            loginModal.style.display = 'block';
        });
    }
    
    // Join Now buttons redirect to members page
    const joinNowBtns = document.querySelectorAll('.join-now-btn');
    joinNowBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Only prevent default if it's not a direct link (href="#")
            if (btn.getAttribute('href') === '#') {
                e.preventDefault();
                window.location.href = '/members';
            }
        });
    });
    
    // Setup Book Class buttons
    setupBookButtons();
    
    // Handle booking form submission
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const className = document.querySelector('#booking-details .booking-summary h3')?.textContent || 'this class';
            document.getElementById('booking-modal').style.display = 'none';
            showNotification(`You've booked ${className}!`, 'success');
        });
    }
    
    // Close buttons for modals
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// Setup Book Class buttons
function setupBookButtons() {
    const bookClassBtns = document.querySelectorAll('.book-class-btn');
    bookClassBtns.forEach(btn => {
        // Remove existing event listeners by cloning and replacing
        const newBtn = btn.cloneNode(true);
        if (btn.parentNode) {
            btn.parentNode.replaceChild(newBtn, btn);
        }
        
        // Add new event listener
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (e.stopPropagation) {
                e.stopPropagation();
            }
            
            // Get class info
            let className = '';
            let instructor = '';
            let schedule = '';
            
            // Try to find parent card
            const card = this.closest('div');
            if (card) {
                const h3 = card.closest('.class-card') ? 
                    card.closest('.class-card').querySelector('h3') : 
                    card.parentElement.querySelector('h3');
                
                if (h3) {
                    className = h3.textContent.trim();
                }
                
                // Try to get instructor and schedule
                const paragraphs = card.querySelectorAll('p');
                paragraphs.forEach(p => {
                    const text = p.textContent;
                    if (text.includes('Instructor:')) {
                        instructor = text.replace('Instructor:', '').trim();
                    } else if (text.includes('Schedule:')) {
                        schedule = text.replace('Schedule:', '').trim();
                    }
                });
            }
            
            // Set booking details
            const bookingDetails = document.getElementById('booking-details');
            if (bookingDetails) {
                bookingDetails.innerHTML = `
                    <div class="booking-summary">
                        <h3>${className}</h3>
                        <p><strong>Instructor:</strong> ${instructor}</p>
                        <p><strong>Schedule:</strong> ${schedule}</p>
                    </div>
                `;
            }
            
            // Show modal
            const bookingModal = document.getElementById('booking-modal');
            if (bookingModal) {
                bookingModal.style.display = 'block';
            }
        });
    });
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check for logged in user
    const userJson = localStorage.getItem('user');
    if (userJson) {
        try {
            const user = JSON.parse(userJson);
            if (user && user.isLoggedIn) {
                // Update UI for logged-in user
                const loginBtn = document.querySelector('#login-btn');
                if (loginBtn) {
                    loginBtn.textContent = user.name || 'MY ACCOUNT';
                    // Update login button to go to profile page instead
                    loginBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        showNotification('Profile page coming soon!', 'info');
                    }, { once: true });
                }
            }
        } catch (e) {
            console.error('Error parsing user data', e);
            localStorage.removeItem('user');
        }
    }
    
    // Setup modals
    setupModals();
});

// For pages loaded via AJAX or other methods
function initializePage() {
    setupModals();
}

// Call initialization function for immediate loading
initializePage();