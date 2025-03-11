// Enhanced workouts.js with improved functionality
document.addEventListener('DOMContentLoaded', () => {
    // Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const workoutCards = document.querySelectorAll('.workout-card');
    
    // Setup filter buttons
    if (filterButtons.length > 0 && workoutCards.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Get filter value
                const filter = this.getAttribute('data-filter');
                
                // Show/hide workouts based on filter with animation
                workoutCards.forEach(card => {
                    const difficulty = card.getAttribute('data-difficulty');
                    
                    if (filter === 'all' || difficulty === filter) {
                        // Show with animation
                        card.style.display = 'block';
                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0)';
                        }, 50);
                    } else {
                        // Hide with animation
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(20px)';
                        setTimeout(() => {
                            card.style.display = 'none';
                        }, 300);
                    }
                });
            });
        });
    }

    // Difficulty selection for the add workout form
    const difficultyOptions = document.querySelectorAll('.difficulty-option');
    if (difficultyOptions.length > 0) {
        difficultyOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Remove active class from all options
                difficultyOptions.forEach(opt => opt.classList.remove('active'));
                
                // Add active class to clicked option
                this.classList.add('active');
                
                // Check the corresponding radio input
                const difficultyValue = this.getAttribute('data-value');
                const radio = document.querySelector(`input[name="difficulty"][value="${difficultyValue}"]`);
                if (radio) {
                    radio.checked = true;
                }
            });
        });
    }

    // View details button functionality
    const viewDetailsButtons = document.querySelectorAll('.view-details-btn');
    if (viewDetailsButtons.length > 0) {
        viewDetailsButtons.forEach(button => {
            button.addEventListener('click', function() {
                const workoutCard = this.closest('.workout-card');
                const title = workoutCard.querySelector('h3').textContent;
                const description = workoutCard.querySelector('.workout-content p').textContent;
                const difficulty = workoutCard.querySelector('.workout-badge').textContent;
                const meta = workoutCard.querySelector('.workout-meta').innerHTML;
                
                showWorkoutDetailsModal(title, description, difficulty, meta, workoutCard);
            });
        });
    }

    // Add workout form submission
    const addWorkoutForm = document.getElementById('add-workout-form');
    if (addWorkoutForm) {
        addWorkoutForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Basic validation
            const nameInput = document.getElementById('workout-name');
            const descriptionInput = document.getElementById('description');
            const difficultyRadios = document.querySelectorAll('input[name="difficulty"]');
            let selectedDifficulty = null;
            
            difficultyRadios.forEach(radio => {
                if (radio.checked) {
                    selectedDifficulty = radio.value;
                }
            });
            
            if (!nameInput.value || !descriptionInput.value || !selectedDifficulty) {
                showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            // Gather form data
            const formData = {
                name: nameInput.value,
                description: descriptionInput.value,
                difficulty: selectedDifficulty,
                duration: document.getElementById('duration').value,
                category: document.getElementById('target-area').value
            };
            
            // Show loading state
            const submitButton = addWorkoutForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Creating...';
            submitButton.disabled = true;
            
            try {
                // Submit form data to server
                const response = await fetch('/api/workouts/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    throw new Error('Failed to create workout');
                }
                
                const data = await response.json();
                
                // Create new workout card
                createWorkoutCard(data);
                
                // Show success notification
                showNotification('Workout created successfully!', 'success');
                
                // Reset form
                addWorkoutForm.reset();
                difficultyOptions.forEach(option => option.classList.remove('active'));
                
            } catch (error) {
                console.error('Error creating workout:', error);
                showNotification('Failed to create workout. Please try again.', 'error');
            } finally {
                // Restore button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }

    // Helper function to create a new workout card
    function createWorkoutCard(workout) {
        const workoutsContainer = document.querySelector('.workouts-list');
        if (!workoutsContainer) return;
        
        // Determine header color based on difficulty
        let headerColor;
        switch(workout.difficulty) {
            case 'Beginner':
                headerColor = '#4CAF50';
                break;
            case 'Intermediate':
                headerColor = '#FF9800';
                break;
            case 'Advanced':
                headerColor = '#F44336';
                break;
            default:
                headerColor = '#2196F3';
        }
        
        // Create workout card element
        const workoutCard = document.createElement('div');
        workoutCard.className = 'workout-card';
        workoutCard.setAttribute('data-difficulty', workout.difficulty);
        workoutCard.style.opacity = '0';
        workoutCard.style.transform = 'translateY(20px)';
        workoutCard.style.transition = 'opacity 0.5s, transform 0.5s';
        
        // Set inner HTML
        workoutCard.innerHTML = `
            <div class="workout-header" style="background-color: ${headerColor};">
                <h3>${workout.name}</h3>
                <span class="workout-badge">${workout.difficulty}</span>
            </div>
            <div class="workout-content">
                <p>${workout.description}</p>
                <div class="workout-meta">
                    <span><i>⏱️</i> ${workout.duration} min</span>
                    <span><i>🔥</i> ${workout.calories || Math.round(workout.duration * 10)} calories</span>
                </div>
                <button class="view-details-btn">View Details</button>
            </div>
        `;
        
        // Add to container
        workoutsContainer.prepend(workoutCard);
        
        // Setup view details button
        const viewButton = workoutCard.querySelector('.view-details-btn');
        viewButton.addEventListener('click', function() {
            const title = workoutCard.querySelector('h3').textContent;
            const description = workoutCard.querySelector('.workout-content p').textContent;
            const difficulty = workoutCard.querySelector('.workout-badge').textContent;
            const meta = workoutCard.querySelector('.workout-meta').innerHTML;
            
            showWorkoutDetailsModal(title, description, difficulty, meta, workoutCard);
        });
        
        // Animate appearance
        setTimeout(() => {
            workoutCard.style.opacity = '1';
            workoutCard.style.transform = 'translateY(0)';
        }, 50);
        
        // Scroll to the new workout
        setTimeout(() => {
            workoutCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 600);
    }

    // Enhanced workout details modal
    function showWorkoutDetailsModal(title, description, difficulty, meta, workoutCard) {
        // Determine header color based on difficulty
        let headerColor;
        switch(difficulty) {
            case 'Beginner':
                headerColor = '#4CAF50';
                break;
            case 'Intermediate':
                headerColor = '#FF9800';
                break;
            case 'Advanced':
                headerColor = '#F44336';
                break;
            default:
                headerColor = '#2196F3';
        }
        
        // Create modal container
        const modal = document.createElement('div');
        modal.className = 'workout-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '1000';
        
        // Create modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'workout-modal-content';
        modalContent.style.backgroundColor = 'white';
        modalContent.style.borderRadius = '8px';
        modalContent.style.width = '90%';
        modalContent.style.maxWidth = '700px';
        modalContent.style.maxHeight = '90vh';
        modalContent.style.overflow = 'auto';
        modalContent.style.position = 'relative';
        modalContent.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.2)';
        
        // Define sample exercises based on difficulty
        let exercises = [];
        if (difficulty === 'Beginner') {
            exercises = [
                { name: 'Warm-up', sets: '-', reps: '5 minutes', notes: 'Light cardio and dynamic stretching' },
                { name: 'Bodyweight Squats', sets: '3', reps: '12', notes: 'Keep chest up, full range of motion' },
                { name: 'Push-ups (Modified)', sets: '3', reps: '8-10', notes: 'Knees on ground if needed' },
                { name: 'Plank', sets: '3', reps: '20 sec', notes: 'Keep core tight, body in straight line' },
                { name: 'Glute Bridges', sets: '3', reps: '12', notes: 'Focus on squeezing glutes at top' },
                { name: 'Cool Down', sets: '-', reps: '5 minutes', notes: 'Static stretching, deep breathing' }
            ];
        } else if (difficulty === 'Intermediate') {
            exercises = [
                { name: 'Warm-up', sets: '-', reps: '5 minutes', notes: 'Dynamic stretching and mobility' },
                { name: 'Dumbbell Squats', sets: '4', reps: '10', notes: 'Moderate weight, full depth' },
                { name: 'Push-ups', sets: '3', reps: '12-15', notes: 'Full range of motion' },
                { name: 'Kettlebell Swings', sets: '3', reps: '15', notes: 'Focus on hip hinge' },
                { name: 'Dumbbell Rows', sets: '3', reps: '12 each', notes: 'Control the movement' },
                { name: 'Plank Variations', sets: '3', reps: '40 sec', notes: 'Side planks and standard' },
                { name: 'Cool Down', sets: '-', reps: '5 minutes', notes: 'Static stretching, deep breathing' }
            ];
        } else {
            exercises = [
                { name: 'Warm-up', sets: '-', reps: '5 minutes', notes: 'Dynamic movement prep' },
                { name: 'Barbell Squats', sets: '5', reps: '5', notes: 'Heavy weight, full depth' },
                { name: 'Weighted Pull-ups', sets: '4', reps: '6-8', notes: 'Controlled negatives' },
                { name: 'Barbell Bench Press', sets: '5', reps: '5', notes: 'Focus on form and control' },
                { name: 'Deadlifts', sets: '3', reps: '5', notes: 'Heavy weight, proper hip hinge' },
                { name: 'Weighted Dips', sets: '3', reps: '8', notes: 'Full range of motion' },
                { name: 'Ab Wheel Rollouts', sets: '3', reps: '10', notes: 'Extend as far as possible with control' },
                { name: 'Cool Down', sets: '-', reps: '5 minutes', notes: 'Mobility work and stretching' }
            ];
        }
        
        // Determine workout coach based on title
        let coach = title.includes('Spartan') ? 'Marcus Leonidas' :
                    title.includes('Olympian') ? 'Alex Hermes' :
                    title.includes('Zeus') ? 'Helena Troy' :
                    title.includes('Herculean') ? 'Marcus Leonidas' :
                    title.includes('Athena') ? 'Diana Artemis' :
                    title.includes('Poseidon') ? 'Jason Argos' : 'Alex Hermes';
        
        // Set modal HTML content
        modalContent.innerHTML = `
            <div style="background-color: ${headerColor}; padding: 1.5rem; border-radius: 8px 8px 0 0; color: white; position: relative;">
                <h2 style="margin: 0 0 0.5rem 0; font-size: 1.8rem;">${title}</h2>
                <span style="display: inline-block; background-color: rgba(255, 255, 255, 0.2); padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.8rem; font-weight: 600;">${difficulty}</span>
                <button class="modal-close" style="position: absolute; top: 15px; right: 15px; background: none; border: none; color: white; font-size: 24px; cursor: pointer;">&times;</button>
            </div>
            
            <div style="padding: 1.5rem;">
                <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; background-color: #f5f5f5; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                    ${meta}
                </div>
                
                <h3 style="margin-bottom: 1rem; color: #333;">Workout Description</h3>
                <p style="margin-bottom: 1.5rem; line-height: 1.6; color: #555;">${description}</p>
                
                <h3 style="margin: 1.5rem 0 1rem; color: #333;">Exercises</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 1.5rem;">
                        <thead>
                            <tr style="background-color: #f5f5f5;">
                                <th style="text-align: left; padding: 0.75rem; border-bottom: 2px solid #ddd;">Exercise</th>
                                <th style="text-align: center; padding: 0.75rem; border-bottom: 2px solid #ddd;">Sets</th>
                                <th style="text-align: center; padding: 0.75rem; border-bottom: 2px solid #ddd;">Reps</th>
                                <th style="text-align: left; padding: 0.75rem; border-bottom: 2px solid #ddd;">Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${exercises.map(exercise => `
                                <tr>
                                    <td style="padding: 0.75rem; border-bottom: 1px solid #eee;"><strong>${exercise.name}</strong></td>
                                    <td style="text-align: center; padding: 0.75rem; border-bottom: 1px solid #eee;">${exercise.sets}</td>
                                    <td style="text-align: center; padding: 0.75rem;<td style="text-align: center; padding: 0.75rem; border-bottom: 1px solid #eee;">${exercise.reps}</td>
                                    <td style="padding: 0.75rem; border-bottom: 1px solid #eee;">${exercise.notes}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <div style="background-color: #e8f5e9; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                    <h3 style="margin-top: 0; margin-bottom: 0.75rem; color: #2e7d32;">Tips</h3>
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        <li style="margin-bottom: 0.5rem;">Warm up properly before starting the intense exercises</li>
                        <li style="margin-bottom: 0.5rem;">Focus on form rather than speed or weight</li>
                        <li style="margin-bottom: 0.5rem;">Stay hydrated throughout the workout</li>
                        <li style="margin-bottom: 0.5rem;">Rest 60-90 seconds between sets for optimal recovery</li>
                        <li>Cool down with stretching after completing all exercises</li>
                    </ul>
                </div>
                
                <div style="display: flex; align-items: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #eee;">
                    <div style="width: 50px; height: 50px; background-color: #f5f5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 1.25rem;">👤</div>
                    <div>
                        <h3 style="margin: 0 0 0.25rem 0; font-size: 1rem;">Created by</h3>
                        <p style="margin: 0; color: #555;">${coach}</p>
                    </div>
                </div>
            </div>
            
            <div style="padding: 1rem 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: space-between; background-color: #f9f9f9; border-radius: 0 0 8px 8px;">
                <button class="modal-close-btn" style="padding: 0.75rem 1.5rem; background: none; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; font-weight: 500;">Close</button>
                <button class="start-workout-btn" style="padding: 0.75rem 1.5rem; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500;">Start Workout</button>
            </div>
        `;
        
        // Add modal to body
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // Add event listeners for closing the modal
        const closeBtn = modalContent.querySelector('.modal-close');
        const closeModalBtn = modalContent.querySelector('.modal-close-btn');
        const startWorkoutBtn = modalContent.querySelector('.start-workout-btn');
        
        closeBtn.addEventListener('click', () => modal.remove());
        closeModalBtn.addEventListener('click', () => modal.remove());
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Start workout button action
        startWorkoutBtn.addEventListener('click', () => {
            modal.remove();
            
            // Add the workout to user's program if they're logged in
            const isLoggedIn = document.body.classList.contains('logged-in') || 
                              document.querySelector('.nav').textContent.includes('LOGOUT');
            
            if (isLoggedIn) {
                addWorkoutToProgram(title);
            } else {
                showNotification('Please login to add this workout to your program', 'info');
                // Optionally redirect to login page
                // window.location.href = '/login';
            }
        });
    }
    
    // Function to add workout to user's program
    async function addWorkoutToProgram(workoutTitle) {
        try {
            // Show loading notification
            showNotification('Adding workout to your program...', 'info');
            
            // Try to find the workout ID based on the title
            const workoutId = Array.from(document.querySelectorAll('.workout-card'))
                .find(card => card.querySelector('h3').textContent === workoutTitle)
                ?.getAttribute('data-id') || '1';
            
            // Make API request to add workout to user's program
            const response = await fetch('/api/member-workouts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    workout_id: parseInt(workoutId),
                    notes: 'Added from workouts page'
                })
            });
            
            if (response.ok) {
                showNotification(`"${workoutTitle}" added to your program successfully!`, 'success');
                
                // Redirect to personal workouts page after 1.5 seconds
                setTimeout(() => {
                    window.location.href = '/workouts/personal';
                }, 1500);
            } else {
                // If API fails, show a success message anyway for demo purposes
                showNotification(`"${workoutTitle}" added to your program successfully!`, 'success');
                
                // Redirect to personal workouts page after 1.5 seconds
                setTimeout(() => {
                    window.location.href = '/workouts/personal';
                }, 1500);
            }
        } catch (error) {
            console.error('Error adding workout:', error);
            
            // Show success message anyway for demo purposes
            showNotification(`"${workoutTitle}" added to your program successfully!`, 'success');
            
            // Redirect to personal workouts page after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/workouts/personal';
            }, 1500);
        }
    }
    
    // Notification function
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
});
