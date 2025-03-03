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
            const nameInput = e.target.name;
            const emailInput = e.target.email;
            const passwordInput = e.target.password;
            const membershipInput = e.target.membership_type;
            const termsCheckbox = e.target.terms;
            
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
                phone: e.target.phone ? e.target.phone.value : '', // Optional
                message: e.target.message ? e.target.message.value : '' // Optional fitness goals
            };
            
            // Show loading state
            const submitButton = memberForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitButton.disabled = true;
            
            try {
                console.log('Attempting to send API request');
                console.log('Form Data:', formData);
                
                const newMember = await apiRequest('/api/members', 'POST', formData);
                console.log('API Response:', newMember);
                
                if (newMember) {
                    // Create new member card with animation
                    const memberCard = document.createElement('div');
                    memberCard.className = 'member-card';
                    memberCard.style.opacity = '0';
                    memberCard.style.transform = 'translateY(20px)';
                    
                    memberCard.innerHTML = `
                        <div class="member-avatar">
                            <i class="fas fa-user-circle"></i>
                        </div>
                        <h3>${newMember.name}</h3>
                        <p><i class="fas fa-envelope"></i> ${newMember.email}</p>
                        <p><i class="fas fa-award"></i> ${newMember.membership_type} Membership</p>
                        <p><i class="fas fa-calendar-alt"></i> Joined: ${new Date().toISOString().split('T')[0]}</p>
                        <div class="member-actions">
                            <button class="btn-small"><i class="fas fa-envelope"></i> Message</button>
                            <button class="btn-small"><i class="fas fa-user-plus"></i> Follow</button>
                        </div>
                    `;
                    
                    // Add to the list
                    memberList.appendChild(memberCard);
                    
                    // Animate the new card
                    setTimeout(() => {
                        memberCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        memberCard.style.opacity = '1';
                        memberCard.style.transform = 'translateY(0)';
                    }, 10);
                    
                    // Show success message
                    showNotification('Welcome to Olympus Strength! Your membership has been successfully created.', 'success');
                    
                    // Reset form
                    memberForm.reset();
                    
                    // Scroll to the new member card
                    setTimeout(() => {
                        memberCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
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