// static/js/home.js
document.addEventListener('DOMContentLoaded', () => {
    const classGrid = document.querySelector('.class-grid');
    const loadingElement = document.getElementById('loading');
    
    // Enhanced classes data with more details
    const classes = [
        {
            name: 'Olympic Weightlifting',
            instructor: 'Alex Hermes',
            time: 'Mon, Wed, Fri - 7:00 AM',
            description: 'Master the snatch and clean & jerk with expert technique coaching for maximum power development.',
            level: 'All Levels',
            image: 'weightlifting.jpg'
        },
        {
            name: 'Spartan HIIT',
            instructor: 'Marcus Leonidas',
            time: 'Tue, Thu - 6:00 PM',
            description: 'High-intensity interval training inspired by warrior conditioning to push your limits and maximize calorie burn.',
            level: 'Intermediate',
            image: 'hiit.jpg'
        },
        {
            name: 'Strength Foundations',
            instructor: 'Helena Troy',
            time: 'Mon, Wed - 5:30 PM',
            description: 'Master fundamental lifts with expert coaching to build the foundation for legendary strength.',
            level: 'Beginner',
            image: 'strength.jpg'
        },
        {
            name: 'Atlas Conditioning',
            instructor: 'Diana Artemis',
            time: 'Tue, Thu, Sat - 8:00 AM',
            description: 'Build endurance, strength, and conditioning through varied movement patterns that prepare you for anything.',
            level: 'All Levels',
            image: 'conditioning.jpg'
        },
        {
            name: 'Hercules Challenge',
            instructor: 'Jason Argos',
            time: 'Mon, Wed, Fri - 6:30 PM',
            description: 'Push your limits with this intense functional fitness program inspired by the twelve labors of Hercules.',
            level: 'Advanced',
            image: 'hercules.jpg'
        },
        {
            name: 'Olympian Recovery',
            instructor: 'Athena Wisdom',
            time: 'Tue, Thu - 9:00 AM',
            description: 'Balance strength with mobility through dedicated recovery sessions to enhance performance and prevent injury.',
            level: 'All Levels',
            image: 'recovery.jpg'
        }
    ];
    
    // Display the classes with improved cards
    function displayClasses() {
        loadingElement.style.display = 'none';
        
        classes.forEach(cls => {
            const classCard = document.createElement('div');
            classCard.className = 'class-card';
            
            // Use a placeholder image if needed, or just style the header nicely
            classCard.innerHTML = `
                <h3>${cls.name}</h3>
                <div class="class-card-content">
                    <p><strong>Instructor:</strong> ${cls.instructor}</p>
                    <p><strong>Schedule:</strong> ${cls.time}</p>
                    <p><strong>Level:</strong> ${cls.level}</p>
                    <p>${cls.description}</p>
                    <button class="btn book-class-btn">Book Class</button>
                </div>
            `;
            
            classGrid.appendChild(classCard);
        });
        
        // After adding class cards, refresh modal setup for the new buttons
        setupModals();
    }
    
    // Add scroll animation for the hero button
    const heroButton = document.querySelector('.hero .btn');
    if (heroButton) {
        heroButton.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = document.querySelector(heroButton.getAttribute('href'));
            if (targetSection) {
                window.scrollTo({
                    top: targetSection.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    }
    
    // Simulate loading delay (would be a real API call in production)
    setTimeout(displayClasses, 500);
});