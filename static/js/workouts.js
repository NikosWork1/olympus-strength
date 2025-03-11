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
                    const duration = newWorkout.duration || formData.duration || 45;
                    const calories = newWorkout.calories || Math.round(duration * 10); // Simple calculation
                    
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

// Add this JavaScript to your workouts.js file or in a script tag at the bottom of your workouts.html page

document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners for all View Details buttons
    const viewDetailsButtons = document.querySelectorAll('.workout-card .btn');
    
    viewDetailsButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Prevent navigation if it's a link
            e.preventDefault();
            
            // Get the workout card
            const workoutCard = this.closest('.workout-card');
            
            // Get workout details
            const workoutTitle = workoutCard.querySelector('h3').textContent;
            const workoutDescription = workoutCard.querySelector('p').textContent;
            const workoutDifficulty = workoutCard.querySelector('.workout-badge').textContent;
            
            // Create modal for workout details
            showWorkoutDetailsModal(workoutTitle, workoutDescription, workoutDifficulty, workoutCard);
        });
    });
    
    // Function to show workout details modal
    function showWorkoutDetailsModal(title, description, difficulty, workoutCard) {
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
        
        // Get difficulty color
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
        
        // Try to get additional metadata if available
        let duration = '';
        let calories = '';
        const metaElements = workoutCard.querySelectorAll('.workout-meta span');
        if (metaElements.length > 0) {
            metaElements.forEach(span => {
                if (span.textContent.includes('min')) {
                    duration = span.textContent.trim();
                } else if (span.textContent.includes('calories')) {
                    calories = span.textContent.trim();
                }
            });
        }
        
        // Create modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'workout-modal-content';
        modalContent.style.backgroundColor = 'white';
        modalContent.style.borderRadius = '8px';
        modalContent.style.width = '90%';
        modalContent.style.maxWidth = '600px';
        modalContent.style.maxHeight = '90vh';
        modalContent.style.overflowY = 'auto';
        modalContent.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        modalContent.style.position = 'relative';
        
        // Create modal header with difficulty color
        const modalHeader = document.createElement('div');
        modalHeader.className = 'workout-modal-header';
        modalHeader.style.padding = '1.5rem';
        modalHeader.style.backgroundColor = headerColor;
        modalHeader.style.color = 'white';
        modalHeader.style.borderTopLeftRadius = '8px';
        modalHeader.style.borderTopRightRadius = '8px';
        
        // Add title to header
        const modalTitle = document.createElement('h2');
        modalTitle.textContent = title;
        modalTitle.style.margin = '0';
        modalTitle.style.padding = '0';
        modalHeader.appendChild(modalTitle);
        
        // Add difficulty badge
        const difficultyBadge = document.createElement('span');
        difficultyBadge.textContent = difficulty;
        difficultyBadge.style.display = 'inline-block';
        difficultyBadge.style.padding = '0.25rem 0.75rem';
        difficultyBadge.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        difficultyBadge.style.borderRadius = '20px';
        difficultyBadge.style.fontSize = '0.875rem';
        difficultyBadge.style.marginTop = '0.5rem';
        modalHeader.appendChild(difficultyBadge);
        
        // Create modal body
        const modalBody = document.createElement('div');
        modalBody.className = 'workout-modal-body';
        modalBody.style.padding = '1.5rem';
        
        // Add metadata if available
        if (duration || calories) {
            const metaContainer = document.createElement('div');
            metaContainer.style.display = 'flex';
            metaContainer.style.gap = '1.5rem';
            metaContainer.style.marginBottom = '1.5rem';
            metaContainer.style.backgroundColor = '#f5f5f5';
            metaContainer.style.padding = '1rem';
            metaContainer.style.borderRadius = '6px';
            
            if (duration) {
                const durationDiv = document.createElement('div');
                durationDiv.innerHTML = `<strong>⏱️ Duration:</strong> ${duration.replace('⏱️', '')}`;
                metaContainer.appendChild(durationDiv);
            }
            
            if (calories) {
                const caloriesDiv = document.createElement('div');
                caloriesDiv.innerHTML = `<strong>🔥 Calories:</strong> ${calories.replace('🔥', '')}`;
                metaContainer.appendChild(caloriesDiv);
            }
            
            modalBody.appendChild(metaContainer);
        }
        
        // Add description title
        const descriptionTitle = document.createElement('h3');
        descriptionTitle.textContent = 'Workout Description';
        descriptionTitle.style.marginBottom = '1rem';
        modalBody.appendChild(descriptionTitle);
        
        // Add description text
        const descriptionText = document.createElement('p');
        descriptionText.textContent = description;
        modalBody.appendChild(descriptionText);
        
        // Add exercises section (placeholder - this would be populated with actual workout data)
        const exercisesSection = document.createElement('div');
        exercisesSection.className = 'exercises-section';
        exercisesSection.style.marginTop = '2rem';
        
        const exercisesTitle = document.createElement('h3');
        exercisesTitle.textContent = 'Exercises';
        exercisesTitle.style.marginBottom = '1rem';
        exercisesSection.appendChild(exercisesTitle);
        
        // Sample exercises (in a real implementation, these would come from your database)
        const exercises = [
            { name: 'Warm-up', sets: '-', reps: '5 minutes', notes: 'Light cardio and dynamic stretching' },
            { name: 'Squats', sets: '3', reps: '12', notes: 'Keep chest up, full range of motion' },
            { name: 'Push-ups', sets: '3', reps: '10-15', notes: 'Modify on knees if needed' },
            { name: 'Kettlebell Swings', sets: '3', reps: '15', notes: 'Focus on hip hinge' },
            { name: 'Planks', sets: '3', reps: '30 sec', notes: 'Keep core tight, body in straight line' },
            { name: 'Cool Down', sets: '-', reps: '5 minutes', notes: 'Static stretching, deep breathing' }
        ];
        
        // Create exercise table
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        
        // Add table header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th style="text-align: left; padding: 0.75rem; border-bottom: 2px solid #e0e0e0;">Exercise</th>
                <th style="text-align: center; padding: 0.75rem; border-bottom: 2px solid #e0e0e0;">Sets</th>
                <th style="text-align: center; padding: 0.75rem; border-bottom: 2px solid #e0e0e0;">Reps</th>
                <th style="text-align: left; padding: 0.75rem; border-bottom: 2px solid #e0e0e0;">Notes</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Add table body with exercises
        const tbody = document.createElement('tbody');
        exercises.forEach(exercise => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="padding: 0.75rem; border-bottom: 1px solid #e0e0e0;"><strong>${exercise.name}</strong></td>
                <td style="text-align: center; padding: 0.75rem; border-bottom: 1px solid #e0e0e0;">${exercise.sets}</td>
                <td style="text-align: center; padding: 0.75rem; border-bottom: 1px solid #e0e0e0;">${exercise.reps}</td>
                <td style="padding: 0.75rem; border-bottom: 1px solid #e0e0e0;">${exercise.notes}</td>
            `;
            tbody.appendChild(row);
        });
        table.appendChild(tbody);
        
        exercisesSection.appendChild(table);
        modalBody.appendChild(exercisesSection);
        
        // Add tips section
        const tipsSection = document.createElement('div');
        tipsSection.style.marginTop = '2rem';
        tipsSection.style.backgroundColor = '#e8f5e9';
        tipsSection.style.padding = '1rem';
        tipsSection.style.borderRadius = '6px';
        
        const tipsTitle = document.createElement('h3');
        tipsTitle.textContent = 'Tips';
        tipsTitle.style.marginBottom = '0.5rem';
        tipsSection.appendChild(tipsTitle);
        
        const tipsList = document.createElement('ul');
        tipsList.style.paddingLeft = '1.5rem';
        tipsList.style.marginBottom = '0';
        
        const tips = [
            'Warm up properly before starting the intense exercises',
            'Focus on form rather than speed or weight',
            'Stay hydrated throughout the workout',
            'Rest 60-90 seconds between sets for optimal recovery',
            'Cool down with stretching after completing all exercises'
        ];
        
        tips.forEach(tip => {
            const listItem = document.createElement('li');
            listItem.textContent = tip;
            listItem.style.marginBottom = '0.5rem';
            tipsList.appendChild(listItem);
        });
        
        tipsSection.appendChild(tipsList);
        modalBody.appendChild(tipsSection);
        
        // Add coach section (if workout has assigned coach)
        const coachSection = document.createElement('div');
        coachSection.style.marginTop = '2rem';
        coachSection.style.display = 'flex';
        coachSection.style.alignItems = 'center';
        coachSection.style.gap = '1rem';
        
        const coachAvatar = document.createElement('div');
        coachAvatar.style.width = '50px';
        coachAvatar.style.height = '50px';
        coachAvatar.style.borderRadius = '50%';
        coachAvatar.style.backgroundColor = '#e0e0e0';
        coachAvatar.style.display = 'flex';
        coachAvatar.style.alignItems = 'center';
        coachAvatar.style.justifyContent = 'center';
        coachAvatar.style.fontWeight = 'bold';
        coachAvatar.textContent = '👤';
        
        const coachInfo = document.createElement('div');
        
        const coachTitle = document.createElement('h3');
        coachTitle.style.margin = '0';
        coachTitle.style.marginBottom = '0.25rem';
        coachTitle.textContent = 'Created by';
        
        const coachName = document.createElement('p');
        coachName.style.margin = '0';
        coachName.textContent = 'Alex Hermes';
        
        coachInfo.appendChild(coachTitle);
        coachInfo.appendChild(coachName);
        
        coachSection.appendChild(coachAvatar);
        coachSection.appendChild(coachInfo);
        
        modalBody.appendChild(coachSection);
        
        // Create modal footer
        const modalFooter = document.createElement('div');
        modalFooter.className = 'workout-modal-footer';
        modalFooter.style.padding = '1rem 1.5rem';
        modalFooter.style.borderTop = '1px solid #e0e0e0';
        modalFooter.style.display = 'flex';
        modalFooter.style.justifyContent = 'space-between';
        
        // Add close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.className = 'btn btn-outline';
        closeButton.style.padding = '0.5rem 1rem';
        closeButton.style.borderRadius = '4px';
        closeButton.style.border = '1px solid #e0e0e0';
        closeButton.style.background = 'none';
        closeButton.style.cursor = 'pointer';
        
        // Add start workout button
        const startButton = document.createElement('button');
        startButton.textContent = 'Start Workout';
        startButton.className = 'btn';
        startButton.style.padding = '0.5rem 1rem';
        startButton.style.borderRadius = '4px';
        startButton.style.backgroundColor = '#4CAF50';
        startButton.style.color = 'white';
        startButton.style.border = 'none';
        startButton.style.cursor = 'pointer';
        
        modalFooter.appendChild(closeButton);
        modalFooter.appendChild(startButton);
        
        // Assemble modal
        modalContent.appendChild(modalHeader);
        modalContent.appendChild(modalBody);
        modalContent.appendChild(modalFooter);
        modal.appendChild(modalContent);
        
        // Add to body
        document.body.appendChild(modal);
        
        // Close modal when clicking outside or on close button
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        closeButton.addEventListener('click', function() {
            modal.remove();
        });
        
        // Handle start workout button
        startButton.addEventListener('click', function() {
            // In a real app, this would start the workout or navigate to a workout page
            modal.remove();
            showNotification('Workout started! Let\'s get to work!', 'success');
        });
    }
});
    });
});
