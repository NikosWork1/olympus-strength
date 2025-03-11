// Add these functions to a new file: static/js/admin-workouts.js

document.addEventListener('DOMContentLoaded', () => {
    // Load workouts list when the Workouts menu item is clicked
    document.querySelector('#workouts-menu-item').addEventListener('click', loadWorkoutsManagement);
    
    // Setup workout actions if we're on the workouts page
    if (document.querySelector('#workouts-container')) {
        setupWorkoutActions();
    }
});

// Function to load the workouts management UI
function loadWorkoutsManagement() {
    const contentArea = document.querySelector('#admin-content-area');
    
    // Show loading state
    contentArea.innerHTML = '<div class="loading">Loading workouts...</div>';
    
    // Fetch workouts data from API
    fetch('/api/workouts')
        .then(response => response.json())
        .then(workouts => {
            // Generate workouts table UI
            let workoutsHTML = `
                <div id="workouts-container">
                    <div class="admin-header">
                        <h2>Workouts Management</h2>
                        <button id="add-workout-btn" class="btn">Add New Workout</button>
                    </div>
                    
                    <div class="search-filter">
                        <input type="text" id="search-workouts" placeholder="Search workouts...">
                        <select id="difficulty-filter">
                            <option value="">All Difficulty Levels</option>
                            <option value="Beginner">Beginner</option>
                            <option value="Intermediate">Intermediate</option>
                            <option value="Advanced">Advanced</option>
                        </select>
                    </div>
                    
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Difficulty</th>
                                <th>Duration</th>
                                <th>Category</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            workouts.forEach(workout => {
                workoutsHTML += `
                    <tr data-id="${workout.id}">
                        <td>${workout.id}</td>
                        <td>${workout.name}</td>
                        <td>${workout.difficulty}</td>
                        <td>${workout.duration} min</td>
                        <td>${workout.category || 'General'}</td>
                        <td>
                            <button class="action-btn edit-workout" data-id="${workout.id}">✏️</button>
                            <button class="action-btn delete-workout" data-id="${workout.id}">🗑️</button>
                            <button class="action-btn view-workout" data-id="${workout.id}">👁️</button>
                        </td>
                    </tr>
                `;
            });
            
            workoutsHTML += `
                        </tbody>
                    </table>
                </div>
                
                <!-- Workout Form Modal -->
                <div id="workout-modal" class="modal">
                    <div class="modal-content">
                        <span class="close-modal">&times;</span>
                        <h2 id="modal-title">Add New Workout</h2>
                        
                        <form id="workout-form">
                            <input type="hidden" id="workout-id">
                            
                            <div class="form-group">
                                <label for="workout-name">Workout Name</label>
                                <input type="text" id="workout-name" name="name" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="description">Description</label>
                                <textarea id="description" name="description" rows="4" required></textarea>
                            </div>
                            
                            <div class="form-group">
                                <label>Difficulty Level</label>
                                <div class="difficulty-options">
                                    <div class="difficulty-option beginner" data-value="Beginner">
                                        <h4>Beginner</h4>
                                        <p>For those new to fitness</p>
                                        <input type="radio" name="difficulty" value="Beginner" style="display: none;" required>
                                    </div>
                                    <div class="difficulty-option intermediate" data-value="Intermediate">
                                        <h4>Intermediate</h4>
                                        <p>For regular gym-goers</p>
                                        <input type="radio" name="difficulty" value="Intermediate" style="display: none;">
                                    </div>
                                    <div class="difficulty-option advanced" data-value="Advanced">
                                        <h4>Advanced</h4>
                                        <p>For experienced athletes</p>
                                        <input type="radio" name="difficulty" value="Advanced" style="display: none;">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="duration">Duration (minutes)</label>
                                    <input type="number" id="duration" name="duration" min="5" max="120" value="45">
                                </div>
                                
                                <div class="form-group">
                                    <label for="target-area">Primary Target Area</label>
                                    <select id="target-area" name="category">
                                        <option value="Full Body">Full Body</option>
                                        <option value="Upper Body">Upper Body</option>
                                        <option value="Lower Body">Lower Body</option>
                                        <option value="Core">Core</option>
                                        <option value="Cardio">Cardio</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="form-actions">
                                <button type="button" id="cancel-workout">Cancel</button>
                                <button type="submit" id="save-workout">Save Workout</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- Delete Confirmation Modal -->
                <div id="delete-workout-modal" class="modal">
                    <div class="modal-content">
                        <span class="close-modal">&times;</span>
                        <h2>Confirm Deletion</h2>
                        <p>Are you sure you want to delete this workout? This action cannot be undone.</p>
                        <input type="hidden" id="delete-workout-id">
                        <div class="modal-actions">
                            <button id="cancel-delete-workout">Cancel</button>
                            <button id="confirm-delete-workout">Delete Workout</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Update the content area
            contentArea.innerHTML = workoutsHTML;
            
            // Setup event handlers
            setupWorkoutActions();
        })
        .catch(error => {
            contentArea.innerHTML = `<div class="error">Error loading workouts: ${error.message}</div>`;
        });
}

// Setup all workout action event handlers
function setupWorkoutActions() {
    // Implement similar functionality as in the members section
    // (add, edit, delete, view, search, filter)
    // ...
}
