// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const body = document.body;

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'dark';
body.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

function updateThemeIcon(theme) {
    themeIcon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const sidebar = document.getElementById('sidebar');

mobileMenuBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});

// Daily Message / AI Personalization
const userIdInput = document.getElementById('userIdInput');
const refreshBtn = document.getElementById('refreshBtn');
const dailyMessageText = document.getElementById('dailyMessageText');

const dailyMessages = [
    "Today's Challenge: Complete a 30-minute full-body workout focusing on strength and endurance. Push yourself to new limits!",
    "Today's Challenge: Focus on core strength with 3 sets of planks and 100 crunches. Build that six-pack!",
    "Today's Challenge: Cardio day! Run 5km or complete 30 minutes of high-intensity interval training.",
    "Today's Challenge: Upper body strength - 4 sets of push-ups, pull-ups, and shoulder presses.",
    "Today's Challenge: Lower body power - Squats, lunges, and deadlifts. Build those legs!",
    "Today's Challenge: Flexibility and recovery - 20 minutes of yoga and stretching exercises.",
    "Today's Challenge: Full body circuit training - 5 rounds of your favorite exercises!"
];

refreshBtn.addEventListener('click', () => {
    const userId = userIdInput.value.trim();
    
    if (userId) {
        const randomMessage = dailyMessages[Math.floor(Math.random() * dailyMessages.length)];
        dailyMessageText.textContent = `[User ${userId}] ${randomMessage}`;
    } else {
        const randomMessage = dailyMessages[Math.floor(Math.random() * dailyMessages.length)];
        dailyMessageText.textContent = randomMessage;
    }
    
    // Animation
    dailyMessageText.style.opacity = '0.5';
    setTimeout(() => {
        dailyMessageText.style.opacity = '1';
    }, 300);
    
    refreshBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        refreshBtn.style.transform = 'scale(1)';
    }, 150);
});

userIdInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        refreshBtn.click();
    }
});

// Workout Selector Pills
const selectorPills = document.querySelectorAll('.selector-pill');
selectorPills.forEach(pill => {
    pill.addEventListener('click', () => {
        selectorPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
    });
});

// BMI Calculator with Dynamic Status
const weightSlider = document.getElementById('weightSlider');
const heightSlider = document.getElementById('heightSlider');
const weightValue = document.getElementById('weightValue');
const heightValue = document.getElementById('heightValue');
const bmiValue = document.getElementById('bmiValue');
const bmiBadge = document.getElementById('bmiBadge');
const gaugeFill = document.getElementById('gaugeFill');

function calculateBMI() {
    const weight = parseFloat(weightSlider.value);
    const height = parseFloat(heightSlider.value) / 100; // Convert to meters
    const bmi = (weight / (height * height)).toFixed(1);
    bmiValue.textContent = bmi;
    
    // Update gauge (0-100% based on BMI 15-35 range)
    const bmiPercent = Math.max(0, Math.min(100, ((bmi - 15) / (35 - 15)) * 100));
    const circumference = 2 * Math.PI * 70; // radius = 70
    const offset = circumference - (circumference * bmiPercent / 100);
    gaugeFill.style.strokeDashoffset = offset;
    
    // Update badge and color based on BMI
    let status, statusClass, gaugeColor;
    
    if (bmi < 18.5) {
        status = "Underweight";
        statusClass = "underweight";
        gaugeColor = "#fbbf24";
    } else if (bmi >= 18.5 && bmi < 25) {
        status = "You're Healthy";
        statusClass = "healthy";
        gaugeColor = "#10b981";
    } else if (bmi >= 25 && bmi < 30) {
        status = "Overweight";
        statusClass = "overweight";
        gaugeColor = "#f97316";
    } else {
        status = "Obese";
        statusClass = "obese";
        gaugeColor = "#ef4444";
    }
    
    bmiBadge.textContent = status;
    bmiBadge.className = `bmi-badge ${statusClass}`;
    
    // Update gauge color
    const gradient = document.querySelector('#gaugeGradient');
    if (statusClass === 'underweight') {
        gradient.innerHTML = '<stop offset="0%" style="stop-color:#fbbf24;stop-opacity:1" /><stop offset="100%" style="stop-color:#f59e0b;stop-opacity:1" />';
    } else if (statusClass === 'healthy') {
        gradient.innerHTML = '<stop offset="0%" style="stop-color:#10b981;stop-opacity:1" /><stop offset="100%" style="stop-color:#059669;stop-opacity:1" />';
    } else if (statusClass === 'overweight') {
        gradient.innerHTML = '<stop offset="0%" style="stop-color:#f97316;stop-opacity:1" /><stop offset="100%" style="stop-color:#ea580c;stop-opacity:1" />';
    } else {
        gradient.innerHTML = '<stop offset="0%" style="stop-color:#ef4444;stop-opacity:1" /><stop offset="100%" style="stop-color:#dc2626;stop-opacity:1" />';
    }
}

weightSlider.addEventListener('input', () => {
    weightValue.textContent = weightSlider.value + ' Kg';
    calculateBMI();
});

heightSlider.addEventListener('input', () => {
    heightValue.textContent = heightSlider.value + ' cm';
    calculateBMI();
});

// Muscle Group Interactions
const muscleGroups = document.querySelectorAll('.muscle-group');
const muscleName = document.getElementById('muscleName');
const muscleValue = document.getElementById('muscleValue');
const graphLine = document.getElementById('graphLine');
const activationCard = document.getElementById('activationCard');

const muscleData = {
    head: { name: 'Neck Activation', value: 50 },
    chest: { name: 'Chest Activation', value: 75 },
    core: { name: 'Core Activation', value: 60 },
    leftarm: { name: 'Left Arm Activation', value: 85 },
    rightarm: { name: 'Right Arm Activation', value: 85 },
    leftleg: { name: 'Left Leg Activation', value: 90 },
    rightleg: { name: 'Right Leg Activation', value: 88 }
};

function generateGraphData() {
    const points = [];
    for (let i = 0; i <= 10; i++) {
        const x = i * 22;
        const y = 40 + Math.sin(i * 0.5) * 12 + Math.random() * 6;
        points.push(`${x},${y}`);
    }
    return points.join(' ');
}

function updateMuscleCard(muscle) {
    const data = muscleData[muscle];
    if (data) {
        muscleName.textContent = data.name;
        muscleValue.textContent = data.value + '%';
        graphLine.setAttribute('points', generateGraphData());
        
        // Animation
        activationCard.style.transform = 'scale(1.05)';
        setTimeout(() => {
            activationCard.style.transform = 'scale(1)';
        }, 200);
    }
}

muscleGroups.forEach(group => {
    group.addEventListener('mouseenter', () => {
        const muscle = group.getAttribute('data-muscle');
        updateMuscleCard(muscle);
    });
    
    group.addEventListener('mouseleave', () => {
        // Reset to default
        muscleName.textContent = 'Overall Body';
        muscleValue.textContent = '72%';
        graphLine.setAttribute('points', generateGraphData());
    });
});

// Initialize with default chest
updateMuscleCard('chest');

// Dynamic Data Updates
function updateMetrics() {
    // Heart Rate fluctuation
    const heartRate = document.getElementById('heartRateValue');
    const currentHR = parseInt(heartRate.textContent);
    const change = Math.floor(Math.random() * 5) - 2;
    const newHR = Math.max(60, Math.min(200, currentHR + change));
    heartRate.textContent = newHR;
    
    // Calories slight increase
    const calories = document.getElementById('caloriesValue');
    if (Math.random() > 0.7) {
        const currentCal = parseInt(calories.textContent.replace(',', ''));
        calories.textContent = (currentCal + Math.floor(Math.random() * 3)).toLocaleString();
    }
    
    // Update muscle activation graph continuously
    if (graphLine) {
        graphLine.setAttribute('points', generateGraphData());
    }
}

setInterval(updateMetrics, 3000);

// Notification Button
const notificationBtn = document.getElementById('notificationBtn');
notificationBtn.addEventListener('click', () => {
    notificationBtn.style.transform = 'scale(0.9)';
    setTimeout(() => {
        notificationBtn.style.transform = 'scale(1)';
    }, 150);
    // In a real app, this would open a notification panel
    console.log('Notifications clicked');
});

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.querySelector('.search-input').focus();
    }
    
    // Ctrl/Cmd + D for theme toggle
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        themeToggle.click();
    }
});

// Initialize BMI calculation
calculateBMI();

// Smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Set active navigation link based on current page
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Remove all active classes first
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Determine which page we're on and set active accordingly
    if (currentPage.includes('index.html') || currentPage === '' || currentPath.includes('Mainpage')) {
        // Dashboard page
        const dashboardLink = Array.from(navLinks).find(link => 
            link.textContent.includes('Dashboard') || link.getAttribute('href') === '#' || 
            link.getAttribute('href').includes('index.html')
        );
        if (dashboardLink) dashboardLink.classList.add('active');
    } else if (currentPage.includes('nutrients.html') || currentPath.includes('Nutrients')) {
        // Nutrition page
        const nutritionLink = Array.from(navLinks).find(link => 
            link.textContent.includes('Nutrition') || link.getAttribute('href').includes('nutrients')
        );
        if (nutritionLink) nutritionLink.classList.add('active');
    }
}

// Add loading animation
document.addEventListener('DOMContentLoaded', () => {
    setActiveNavLink();
    
    const sections = document.querySelectorAll('.ai-section, .main-grid, .recovery-section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
