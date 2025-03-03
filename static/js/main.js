// static/js/main.js
// Common JavaScript functions used across the site

// Helper function to make API requests
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }

    try {
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
    // Check if modals already exist
    if (document.getElementById('login-modal') && document.getElementById('booking-modal')) {
        return;
    }
    
    // Create login modal
    const loginModal = document.createElement('div');
    loginModal.id = 'login-modal';
    loginModal.className = 'modal';
    loginModal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>Login to Olympus Strength</h2>
            <form id="login-form" class="form">
                <div class="form-group">
                    <label for="login-email">Email</label>
                    <input type="email" id="login-email" required>
                </div>
                <div class="form-group">
                    <label for="login-password">Password</label>
                    <input type="password" id="login-password" required>
                </div>
                <div class="form-check">
                    <input type="checkbox" id="remember-me">
                    <label for="remember-me">Remember me</label>
                </div>
                <button type="submit" class="btn">Login</button>
                <p class="form-footer">Don't have an account? <a href="/members" class="link">Join now</a></p>
            </form>
        </div>
    `;
    
    // Create booking modal
    const bookingModal = document.createElement('div');
    bookingModal.id = 'booking-modal';
    bookingModal.className = 'modal';
    bookingModal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>Book Your Class</h2>
            <div id="booking-details"></div>
            <form id="booking-form" class="form">
                <div class="form-group">
                    <label for="booking-name">Full Name</label>
                    <input type="text" id="booking-name" required>
                </div>
                <div class="form-group">
                    <label for="booking-email">Email</label>
                    <input type="email" id="booking-email" required>
                </div>
                <div class="form-group">
                    <label for="booking-phone">Phone Number</label>
                    <input type="tel" id="booking-phone" required>
                </div>
                <button type="submit" class="btn">Confirm Booking</button>
            </form>
        </div>
    `;
    
    // Add modals to the body
    document.body.appendChild(loginModal);
    document.body.appendChild(bookingModal);
}

// Modal functionality
function setupModals() {
    // Create modals if they don't exist
    createModals();
    
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
            e.preventDefault();
            window.location.href = '/members';
        });
    });
    
    // Setup Book Class buttons
    setupBookButtons();
    
    // Handle login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('login-modal').style.display = 'none';
            showNotification('Login successful! Welcome back to Olympus Strength.', 'success');
        });
    }
    
    // Handle booking form submission
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const className = document.querySelector('#booking-details .booking-summary h3').textContent;
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
        btn.parentNode.replaceChild(newBtn, btn);
        
        // Add new event listener
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
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

// Add styles
function addStyles() {
    // Add notification styles
    let styleElement = document.getElementById('notification-styles');
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'notification-styles';
        styleElement.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }
            
            .notification {
                margin-bottom: 10px;
                padding: 15px 20px;
                border-radius: 4px;
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                position: relative;
                min-width: 250px;
            }
            
            .notification.success {
                background-color: #4CAF50;
            }
            
            .notification.error {
                background-color: #F44336;
            }
            
            .notification.info {
                background-color: #2196F3;
            }
            
            .notification-close {
                position: absolute;
                top: 5px;
                right: 10px;
                background: transparent;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
            }
        `;
        document.head.appendChild(styleElement);
    }
    
    // Add modal styles
    styleElement = document.getElementById('modal-styles');
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'modal-styles';
        styleElement.textContent = `
            .modal {
                display: none;
                position: fixed;
                z-index: 1050;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0, 0, 0, 0.7);
            }
            
            .modal-content {
                background-color: white;
                margin: 10% auto;
                padding: 2rem;
                border-radius: 8px;
                max-width: 500px;
                position: relative;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                animation: modalFadeIn 0.3s;
            }
            
            @keyframes modalFadeIn {
                from { opacity: 0; transform: translateY(-50px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .close-modal {
                position: absolute;
                top: 15px;
                right: 15px;
                font-size: 24px;
                font-weight: bold;
                color: #aaa;
                cursor: pointer;
                background: none;
                border: none;
                padding: 0;
            }
            
            .close-modal:hover {
                color: #333;
            }
            
            .booking-summary {
                background-color: #f5f5f5;
                padding: 1.5rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
            }
            
            .booking-summary h3 {
                margin-bottom: 1rem;
                color: #212121;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 0.5rem;
            }
            
            .form-footer {
                text-align: center;
                margin-top: 1.5rem;
                font-size: 0.9rem;
            }
            
            .form-footer a {
                color: #4CAF50;
                text-decoration: none;
            }
            
            .form-footer a:hover {
                text-decoration: underline;
            }
        `;
        document.head.appendChild(styleElement);
    }
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add styles
    addStyles();
    
    // Setup modals
    setupModals();
});

// For pages loaded via AJAX or other methods
// We need to ensure the setup happens
function initializePage() {
    addStyles();
    setupModals();
}

// Call initialization function for immediate loading
initializePage();