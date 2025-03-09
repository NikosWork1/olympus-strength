// static/js/members.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Members script loaded');
    
    const memberForm = document.getElementById('member-form');
    const membersGrid = document.querySelector('.members-grid');
    
    if (memberForm) {
        console.log('Member form found, setting up submission handler');
        
        memberForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Form validation
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const membershipInput = document.getElementById('membership');
            
            if (!nameInput || !emailInput || !passwordInput || !membershipInput) {
                console.error('Required form elements not found');
                return;
            }
            
            if (!nameInput.value || !emailInput.value || !passwordInput.value || !membershipInput.value) {
                console.error('Form validation failed');
                showNotification('Please fill in all required fields.', 'error');
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
                console.log('Sending API request');
                
                const response = await fetch('/api/members', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to create member');
                }
                
                const data = await response.json();
                console.log('API Response:', data);
                
                if (membersGrid) {
                    // Create new member card with animation
                    const memberCard = document.createElement('div');
                    memberCard.className = 'member-card';
                    memberCard.style.opacity = '0';
                    memberCard.style.transform = 'translateY(20px)';
                    
                    memberCard.innerHTML = `
                        <div class="member-avatar">
                            <i>👤</i>
                        </div>
                        <div class="member-info">
                            <h3 class="member-name">${data.name}</h3>
                            <div class="member-detail">
                                <i>📧</i> ${data.email}
                            </div>
                            <div class="member-detail">
                                <i>🏅</i> ${data.membership_type} Membership
                            </div>
                            <div class="member-actions">
                                <button class="btn btn-sm btn-outline">Message</button>
                                <button class="btn btn-sm">Follow</button>
                            </div>
                        </div>
                    `;
                    
                    // Add to the grid
                    membersGrid.appendChild(memberCard);
                    
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
                
                // Reload page after short delay
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
                
            } catch (error) {
                console.error('Error creating member:', error);
                showNotification(error.message || 'Error creating membership. Please try again.', 'error');
            } finally {
                // Restore button state
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            }
        });
    }
    
    // Add event listeners to message and follow buttons
    document.addEventListener('click', (e) => {
        const messageBtn = e.target.closest('.btn-outline');
        if (messageBtn && messageBtn.textContent.includes('Message')) {
            e.preventDefault();
            const memberCard = messageBtn.closest('.member-card');
            const memberName = memberCard.querySelector('.member-name').textContent;
            showNotification(`Message feature for ${memberName} will be available soon!`, 'info');
        }
        
        const followBtn = e.target.closest('.btn:not(.btn-outline)');
        if (followBtn && followBtn.textContent.includes('Follow')) {
            e.preventDefault();
            const memberCard = followBtn.closest('.member-card');
            const memberName = memberCard.querySelector('.member-name').textContent;
            followBtn.textContent = 'Following';
            followBtn.classList.add('following');
            showNotification(`You are now following ${memberName}!`, 'success');
        }
    });
    
    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput && membersGrid) {
        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.toLowerCase();
            const memberCards = membersGrid.querySelectorAll('.member-card');
            
            memberCards.forEach(card => {
                const name = card.querySelector('.member-name').textContent.toLowerCase();
                const email = card.querySelector('.member-detail').textContent.toLowerCase();
                
                if (name.includes(searchTerm) || email.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});