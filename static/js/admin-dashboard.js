// static/js/admin-dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the dashboard
    initAdminDashboard();
    
    // Set up menu click events
    setupMenuNavigation();
});

function initAdminDashboard() {
    // Load overview data
    loadDashboardOverview();
}

function setupMenuNavigation() {
    // Get all menu items
    const menuItems = document.querySelectorAll('.admin-menu-item');
    
    // Add click event to each menu item
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all menu items
            menuItems.forEach(mi => mi.classList.remove('active'));
            
            // Add active class to clicked menu item
            this.classList.add('active');
            
            // Get the menu item ID to determine which section to load
            const menuId = this.id;
            
            // Load the appropriate section based on menu item
            switch(menuId) {
                case 'overview-menu-item':
                    loadDashboardOverview();
                    break;
                case 'members-menu-item':
                    loadMembersManagement();
                    break;
                case 'workouts-menu-item':
                    loadWorkoutsManagement();
                    break;
                case 'classes-menu-item':
                    loadClassesManagement();
                    break;
                case 'finances-menu-item':
                    loadFinancesManagement();
                    break;
                case 'settings-menu-item':
                    loadSettingsManagement();
                    break;
            }
        });
    });
}

function loadDashboardOverview() {
    const contentArea = document.querySelector('#admin-content-area');
    
    // Show loading state
    contentArea.innerHTML = '<div class="loading">Loading dashboard data...</div>';
    
    // Fetch dashboard data
    Promise.all([
        fetch('/api/stats/members').then(res => res.json()),
        fetch('/api/stats/workouts').then(res => res.json()),
        fetch('/api/stats/classes').then(res => res.json()),
        fetch('/api/stats/retention').then(res => res.json()),
        fetch('/api/activity').then(res => res.json())
    ])
    .then(([members, workouts, classes, retention, activity]) => {
        // Format the data for display
        const overviewHTML = `
            <div class="dashboard-overview">
                <div class="stats-row">
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-value">${members.total}</div>
                        <div class="stat-label">TOTAL MEMBERS</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">💪</div>
                        <div class="stat-value">${workouts.total}</div>
                        <div class="stat-label">WORKOUTS</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">📅</div>
                        <div class="stat-value">${classes.total}</div>
                        <div class="stat-label">CLASSES</div>
                    </div>
                </div>
                
                <div class="stats-row">
                    <div class="stat-card">
                        <div class="stat-icon">📈</div>
                        <div class="stat-value">${retention.rate}%</div>
                        <div class="stat-label">RETENTION RATE</div>
                    </div>
                </div>
                
                <div class="recent-activity">
                    <h2>Recent Activity</h2>
                    <div class="activity-list">
                        ${activity.map(item => `
                            <div class="activity-item">
                                <div class="activity-icon">${getActivityIcon(item.type)}</div>
                                <div class="activity-details">
                                    <div class="activity-title">${item.title}</div>
                                    <div class="activity-meta">${item.details} • ${formatTimeAgo(item.timestamp)}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        // Update the content area
        contentArea.innerHTML = overviewHTML;
    })
    .catch(error => {
        contentArea.innerHTML = `<div class="error">Error loading dashboard data: ${error.message}</div>`;
    });
}

// Helper function to get activity icon
function getActivityIcon(type) {
    switch(type) {
        case 'member_registration': return '👥';
        case 'class_booking': return '📅';
        case 'payment': return '💰';
        case 'workout_added': return '💪';
        default: return '📝';
    }
}

// Helper function to format time ago
function formatTimeAgo(timestamp) {
    const now = new Date();
    const date = new Date(timestamp);
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''} ago`;
}
