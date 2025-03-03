// static/js/workouts.js
document.addEventListener('DOMContentLoaded', () => {
    const workoutForm = document.getElementById('add-workout-form');
    const workoutGrid = document.querySelector('.workout-grid');
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const filter = button.getAttribute('data-filter');
            const workoutCards = workoutGrid.querySelectorAll('.workout-card');
            
            workoutCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-difficulty') === filter) {
                    card.style.display = 'block';
                    // Add a small animation
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 50);
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
    
    // Form submission
    workoutForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Basic form validation
        const nameInput = e.target.name;
        const descriptionInput = e.target.description;
        const difficultyInput = e.target.difficulty;
        
        if (!nameInput.value || !descriptionInput.value || !difficultyInput.value) {
            showNotification('Please fill in all required fields.', 'error');
            return;
        }
        
        const formData = {
            name: nameInput.value,
            description: descriptionInput.value,
            difficulty: difficultyInput.value
        };
        
        // Show loading state
        const submitButton = workoutForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        submitButton.disabled = true;
        
        try {
            // Ensure full HTTPS URL for API request
            const apiUrl = `https://${window.location.host}/api/workouts`;
            
            // Make API request to add workout
            const newWorkout = await apiRequest(apiUrl, 'POST', formData);
            
            if (newWorkout) {
                // Create new workout card
                const workoutCard = document.createElement('div');
                workoutCard.className = 'workout-card';
                workoutCard.setAttribute('data-difficulty', newWorkout.difficulty);
                workoutCard.style.opacity = '0';
                workoutCard.style.transform = 'translateY(20px)';
                
                // Set background color based on difficulty
                let headerColor;
                switch(newWorkout.difficulty) {
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
                
                workoutCard.innerHTML = `
                    <div class="workout-card-header" style="background-color: ${headerColor};">
                        <h3>${newWorkout.name}</h3>
                        <span class="difficulty-badge ${newWorkout.difficulty.toLowerCase()}">
                            ${newWorkout.difficulty}
                        </span>
                    </div>
                    <div class="workout-card-content">
                        <p>${newWorkout.description}</p>
                        <div class="workout-details">
                            <span><i class="fas fa-clock"></i> ${e.target.duration ? e.target.duration.value + ' min' : '45-60 min'}</span>
                            <span><i class="fas fa-fire"></i> 400-600 cal</span>
                        </div>
                        <button class="btn view-workout-btn">View Details</button>
                    </div>
                `;
                
                // Add to the grid
                workoutGrid.appendChild(workoutCard);
                
                // Animate the new card
                setTimeout(() => {
                    workoutCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                    workoutCard.style.opacity = '1';
                    workoutCard.style.transform = 'translateY(0)';
                }, 10);
                
                // Show success message
                showNotification('Your workout program has been created!', 'success');
                
                // Reset form
                workoutForm.reset();
                
                // Scroll to the new workout card
                setTimeout(() => {
                    workoutCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        } catch (error) {
            showNotification('Error creating workout. Please try again.', 'error');
            console.error('Error:', error);
        } finally {
            // Restore button state
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        }
    });
    
    // View Details button functionality
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('view-workout-btn')) {
            const workoutName = e.target.closest('.workout-card').querySelector('h3').textContent;
            showNotification(`Detailed view for "${workoutName}" will be available soon!`, 'info');
        }
    });
});