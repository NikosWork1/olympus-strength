// static/js/members.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');
    
    const memberForm = document.getElementById('add-member-form');
    const memberList = document.querySelector('.member-list');
    
    if (memberForm) {
        console.log('Member form found');
        
        memberForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Form submission intercepted');
            
            // Form validation
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const membershipInput = document.getElementById('membership');
            const termsCheckbox = document.getElementById('terms');
            
            // Detailed logging
            console.log('Form elements:', {
                name: nameInput.value,
                email: emailInput.value,
                password: passwordInput.value ? '****' : 'No password',
                membership: membershipInput.value,
                terms: termsCheckbox.checked
            });
            
            if (!nameInput.value || !emailInput.value || !passwordInput.value || !membershipInput.value || !termsCheckbox.checked) {
                console.error('Form validation failed');
                showNotification('Please fill in all required fields and accept the terms.', 'error');
                return;
            }
            
            const formData = {
                name: nameInput.value,
                email: emailInput.value,
                password: passwordInput.value,
                membership_type: membershipInput.value,
                phone: document.getElementById('phone') ? document.getElementById('phone').value : ''
            };
            
            // Show loading state
            const submitButton = memberForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitButton.disabled = true;
            
            try {
                console.log('Attempting to send API request');
                
                const response = await fetch('/api/members', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    console.log('API Response:', data);
                    
                    // Create new member card with animation
                    const memberCard = document.createElement('div');
                    memberCard.className = 'member-card';
                    memberCard.style.opacity = '0';
                    memberCard.style.transform = 'translateY(20px)';
                    
                    memberCard.innerHTML = `
                        <div class="member-avatar">
                            <i class="fas fa-user-circle"></i>
                        </div>
                        <h3>${data.name}</h3>
                        <p><i class="fas fa-envelope"></i> ${data.email}</p>
                        <p><i class="fas fa-award"></i> ${data.membership_type} Membership</p>
                        <p><i class="fas fa-calendar-alt"></i> Joined: ${new Date().toISOString().split('T')[0]}</p>
                        <div class="member-actions">
                            <button class="btn-small"><i class="fas fa-envelope"></i> Message</button>
                            <button class="btn-small"><i class="fas fa-user-plus"></i> Follow</button>
                        </div>
                    `;
                    
                    // Add to the list
                    if (memberList) {
                        memberList.appendChild(memberCard);
                        
                        // Animate the new card
                        setTimeout(() => {
                            memberCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                            memberCard.style.opacity = '1';
                            memberCard.style.transform = 'translateY(0)';
                        }, 10);
                        
                        // Scroll to the new member card
                        setTimeout(() => {
                            memberCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }, 300);
                    }
                    
                    // Show success message
                    showNotification('Welcome to Olympus Strength! Your membership has been successfully created.', 'success');
                    
                    // Reset form
                    memberForm.reset();
                } else {
                    // Handle API errors
                    showNotification(data.detail || 'Error creating membership. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Complete error details:', error);
                showNotification('Error creating membership. Please try again.', 'error');
            } finally {
                // Restore button state
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            }
        });
    } else {
        console.error('Member form NOT found');
    }
    
    // Add event listeners to message and follow buttons
    document.addEventListener('click', (e) => {
        if (e.target.closest('.btn-small')) {
            const button = e.target.closest('.btn-small');
            const memberName = button.closest('.member-card').querySelector('h3').textContent;
            
            if (button.textContent.includes('Message')) {
                showNotification(`Message feature for ${memberName} will be available soon!`, 'info');
            } else if (button.textContent.includes('Follow')) {
                button.innerHTML = '<i class="fas fa-user-check"></i> Following';
                button.classList.add('following');
                showNotification(`You are now following ${memberName}!`, 'success');
            }
        }
    });
});