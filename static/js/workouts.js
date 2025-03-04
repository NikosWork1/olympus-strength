// static/js/workouts.js
document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const workoutGrid = document.querySelector('.workout-grid') || document.querySelector('.workouts-list');
    
    // Filter functionality
    if (filterButtons.length > 0 && workoutGrid) {
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
    }
    
    // Form submission
    const workoutForm = document.getElementById('add-workout-form');
    if (workoutForm) {
        workoutForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Basic form validation
            const nameInput = workoutForm.querySelector('[name="name"]');
            const descriptionInput = workoutForm.querySelector('[name="description"]');
            const difficultyInput = workoutForm.querySelector('[name="difficulty"]');
            
            if (!nameInput || !descriptionInput || !difficultyInput) {
                console.error('Form inputs not found');
                return;
            }
            
            if (!nameInput.value || !descriptionInput.value || !difficultyInput.value) {
                showNotification('Please fill in all required fields.', 'error');
                return;
            }
            
            const formData = {
                name: nameInput.value,
                description: descriptionInput.value,
                difficulty: difficultyInput.value,
                category: workoutForm.querySelector('[name="target_area"]')?.value || ''
            };
            
            // Add duration and calories if available
            const durationInput = workoutForm.querySelector('[name="duration"]');
            if (durationInput && durationInput.value) {
                formData.duration = parseInt(durationInput.value);
            }
            
            // Show loading state
            const submitButton = workoutForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitButton.disabled = true;
            
            try {
                // Make API request to add workout
                const response = await fetch('/api/workouts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                
                const newWorkout = await response.json();
                
                if (newWorkout && workoutGrid) {
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
                    
                    // Format duration and calories
                    const duration = formData.duration || 45;
                    const calories = Math.round(duration * 10); // Simple calculation
                    
                    workoutCard.innerHTML = `
                        <div class="workout-header" style="background-color: ${headerColor};">
                            <h3>${newWorkout.name}</h3>
                            <span class="workout-badge">${newWorkout.difficulty}</span>
                        </div>
                        <div class="workout-content">
                            <p>${newWorkout.description}</p>
                            <div class="workout-meta">
                                <span><i>⏱️</i> ${duration} min</span>
                                <span><i>🔥</i> ${calories} calories</span>
                            </div>
                            <a href="/workouts/${newWorkout.id}" class="btn">View Details</a>
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
    }
    
    // View Details button functionality
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.view-workout-btn');
        if (btn) {
            const workoutName = btn.closest('.workout-card').querySelector('h3').textContent;
            showNotification(`Detailed view for "${workoutName}" will be available soon!`, 'info');
        }
    });
});