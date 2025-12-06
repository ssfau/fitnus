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

// Set today's date as default
const mealDate = document.getElementById('mealDate');
const today = new Date().toISOString().split('T')[0];
mealDate.value = today;

// File Upload Handling
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadPreview = document.getElementById('uploadPreview');
const previewImage = document.getElementById('previewImage');
const removeImage = document.getElementById('removeImage');
const analyzeBtn = document.getElementById('analyzeBtn');

// Click to upload
uploadZone.addEventListener('click', (e) => {
    if (!e.target.closest('.remove-image')) {
        fileInput.click();
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            uploadPreview.style.display = 'block';
            uploadZone.querySelector('.upload-content').style.display = 'none';
            analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

// Remove image
removeImage.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.value = '';
    uploadPreview.style.display = 'none';
    uploadZone.querySelector('.upload-content').style.display = 'flex';
    analyzeBtn.disabled = true;
    mealBreakdown.style.display = 'none';
});

// Drag and drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        fileInput.files = e.dataTransfer.files;
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            uploadPreview.style.display = 'block';
            uploadZone.querySelector('.upload-content').style.display = 'none';
            analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

// Meal Analysis
const loadingContainer = document.getElementById('loadingContainer');
const mealBreakdown = document.getElementById('mealBreakdown');
const mealName = document.getElementById('mealName');
const caloriesValue = document.getElementById('caloriesValue');
const proteinAmount = document.getElementById('proteinAmount');
const carbsAmount = document.getElementById('carbsAmount');
const fatAmount = document.getElementById('fatAmount');
const proteinProgress = document.getElementById('proteinProgress');
const carbsProgress = document.getElementById('carbsProgress');
const fatProgress = document.getElementById('fatProgress');
const addToLogBtn = document.getElementById('addToLogBtn');

// Simulated meal data
const mealData = {
    'Grilled Chicken & Rice': { calories: 450, protein: 40, carbs: 50, fat: 10 },
    'Salmon & Vegetables': { calories: 380, protein: 35, carbs: 25, fat: 18 },
    'Pasta with Meatballs': { calories: 620, protein: 28, carbs: 75, fat: 22 },
    'Caesar Salad': { calories: 320, protein: 15, carbs: 20, fat: 22 },
    'Beef Steak & Potatoes': { calories: 580, protein: 45, carbs: 40, fat: 28 }
};

analyzeBtn.addEventListener('click', () => {
    // Show loading
    loadingContainer.style.display = 'flex';
    mealBreakdown.style.display = 'none';
    analyzeBtn.disabled = true;

    // Simulate API call (2 seconds)
    setTimeout(() => {
        // Hide loading
        loadingContainer.style.display = 'none';
        
        // Get random meal data
        const mealNames = Object.keys(mealData);
        const randomMeal = mealNames[Math.floor(Math.random() * mealNames.length)];
        const data = mealData[randomMeal];
        
        // Update meal breakdown
        mealName.textContent = randomMeal;
        caloriesValue.textContent = data.calories;
        proteinAmount.textContent = data.protein + 'g';
        carbsAmount.textContent = data.carbs + 'g';
        fatAmount.textContent = data.fat + 'g';
        
        // Update progress bars (normalized to 100% max)
        proteinProgress.style.width = Math.min(100, (data.protein / 100) * 100) + '%';
        carbsProgress.style.width = Math.min(100, (data.carbs / 100) * 100) + '%';
        fatProgress.style.width = Math.min(100, (data.fat / 50) * 100) + '%';
        
        // Show breakdown
        mealBreakdown.style.display = 'block';
        analyzeBtn.disabled = false;
    }, 2000);
});

// Daily Stats Tracking
let dailyStats = {
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0
};

const totalCalories = document.getElementById('totalCalories');
const totalProtein = document.getElementById('totalProtein');
const totalCarbs = document.getElementById('totalCarbs');
const totalFat = document.getElementById('totalFat');

// Add to Log
addToLogBtn.addEventListener('click', () => {
    const mealCalories = parseInt(caloriesValue.textContent);
    const mealProtein = parseInt(proteinAmount.textContent);
    const mealCarbs = parseInt(carbsAmount.textContent);
    const mealFat = parseInt(fatAmount.textContent);
    
    // Update daily stats
    dailyStats.calories += mealCalories;
    dailyStats.protein += mealProtein;
    dailyStats.carbs += mealCarbs;
    dailyStats.fat += mealFat;
    
    // Update display
    totalCalories.textContent = dailyStats.calories;
    totalProtein.textContent = dailyStats.protein + 'g';
    totalCarbs.textContent = dailyStats.carbs + 'g';
    totalFat.textContent = dailyStats.fat + 'g';
    
    // Update goal progress
    updateGoalProgress();
    
    // Reset meal breakdown
    mealBreakdown.style.display = 'none';
    fileInput.value = '';
    uploadPreview.style.display = 'none';
    uploadZone.querySelector('.upload-content').style.display = 'flex';
    analyzeBtn.disabled = true;
    
    // Show success animation
    addToLogBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        addToLogBtn.style.transform = 'scale(1)';
    }, 150);
});

// Goal Progress
const goalCalories = 3000; // Hardcoded goal
const currentCaloriesDisplay = document.getElementById('currentCalories');
const goalCaloriesDisplay = document.getElementById('goalCalories');
const goalProgressFill = document.getElementById('goalProgressFill');
const goalFeedback = document.getElementById('goalFeedback');

function updateGoalProgress() {
    const current = dailyStats.calories;
    const goal = goalCalories;
    const percentage = Math.min(100, (current / goal) * 100);
    
    // Update progress bar
    goalProgressFill.style.width = percentage + '%';
    currentCaloriesDisplay.textContent = current;
    
    // Update feedback
    const difference = goal - current;
    if (current < goal) {
        goalFeedback.className = 'goal-feedback under';
        goalFeedback.innerHTML = `<i class="fas fa-info-circle"></i> <span>Need ${difference} more calories to hit goal.</span>`;
    } else {
        goalFeedback.className = 'goal-feedback over';
        goalFeedback.innerHTML = `<i class="fas fa-check-circle"></i> <span>Surplus Reached!</span>`;
    }
}

// Initialize goal display
goalCaloriesDisplay.textContent = goalCalories;
updateGoalProgress();

// AI Meal Planner
const goalFocus = document.getElementById('goalFocus');
const generateMealBtn = document.getElementById('generateMealBtn');
const generatedMeal = document.getElementById('generatedMeal');
const generatedMealName = document.getElementById('generatedMealName');
const generatedMealCalories = document.getElementById('generatedMealCalories');
const recipeList = document.getElementById('recipeList');
const generatedProtein = document.getElementById('generatedProtein');
const generatedCarbs = document.getElementById('generatedCarbs');
const generatedFat = document.getElementById('generatedFat');

const mealSuggestions = {
    'high-protein': {
        name: 'Grilled Chicken Breast & Quinoa',
        calories: 420,
        protein: 50,
        carbs: 35,
        fat: 8,
        recipe: [
            '200g grilled chicken breast',
            '150g cooked quinoa',
            '100g steamed broccoli',
            '1 tbsp olive oil',
            'Lemon & herbs seasoning'
        ]
    },
    'low-carb': {
        name: 'Zucchini Noodles with Turkey',
        calories: 350,
        protein: 35,
        carbs: 15,
        fat: 18,
        recipe: [
            '200g ground turkey',
            '300g zucchini noodles',
            '50g mushrooms',
            '2 tbsp pesto sauce',
            'Parmesan cheese'
        ]
    },
    'pre-workout': {
        name: 'Oatmeal with Banana & Honey',
        calories: 380,
        protein: 12,
        carbs: 65,
        fat: 8,
        recipe: [
            '80g rolled oats',
            '1 medium banana',
            '1 tbsp honey',
            '30g almonds',
            '200ml almond milk'
        ]
    },
    'post-workout': {
        name: 'Salmon Poke Bowl',
        calories: 520,
        protein: 45,
        carbs: 55,
        fat: 15,
        recipe: [
            '200g fresh salmon, cubed',
            '150g brown rice',
            '50g avocado',
            '30g edamame',
            '20g seaweed',
            'Sesame seeds & soy sauce'
        ]
    },
    'weight-loss': {
        name: 'Mediterranean Salad Bowl',
        calories: 320,
        protein: 20,
        carbs: 30,
        fat: 15,
        recipe: [
            '150g mixed greens',
            '100g grilled chicken',
            '50g feta cheese',
            '30g olives',
            '2 tbsp balsamic vinaigrette',
            'Cherry tomatoes & cucumber'
        ]
    },
    'muscle-gain': {
        name: 'Beef & Sweet Potato Bowl',
        calories: 680,
        protein: 55,
        carbs: 70,
        fat: 20,
        recipe: [
            '250g lean beef steak',
            '200g roasted sweet potato',
            '100g green beans',
            '1 tbsp butter',
            'Garlic & herbs'
        ]
    }
};

generateMealBtn.addEventListener('click', () => {
    const focus = goalFocus.value;
    const meal = mealSuggestions[focus];
    
    if (meal) {
        generatedMealName.textContent = meal.name;
        generatedMealCalories.textContent = meal.calories + ' kcal';
        generatedProtein.textContent = meal.protein + 'g';
        generatedCarbs.textContent = meal.carbs + 'g';
        generatedFat.textContent = meal.fat + 'g';
        
        // Update recipe list
        recipeList.innerHTML = '';
        meal.recipe.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            recipeList.appendChild(li);
        });
        
        // Show generated meal
        generatedMeal.style.display = 'block';
        
        // Animation
        generateMealBtn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            generateMealBtn.style.transform = 'scale(1)';
        }, 150);
    }
});

// Notification Button
const notificationBtn = document.getElementById('notificationBtn');
notificationBtn.addEventListener('click', () => {
    notificationBtn.style.transform = 'scale(0.9)';
    setTimeout(() => {
        notificationBtn.style.transform = 'scale(1)';
    }, 150);
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
    const currentPage = currentPath.split('/').pop() || 'nutrients.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Remove all active classes first
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Determine which page we're on and set active accordingly
    if (currentPage.includes('nutrients.html') || currentPath.includes('Nutrients')) {
        // Nutrition page - set Nutrition link as active
        const nutritionLink = Array.from(navLinks).find(link => 
            link.textContent.includes('Nutrition') || link.getAttribute('href').includes('nutrients')
        );
        if (nutritionLink) nutritionLink.classList.add('active');
    } else if (currentPage.includes('index.html') || currentPath.includes('Mainpage')) {
        // Dashboard page
        const dashboardLink = Array.from(navLinks).find(link => 
            link.textContent.includes('Dashboard') || link.getAttribute('href').includes('index.html')
        );
        if (dashboardLink) dashboardLink.classList.add('active');
    }
}

// Add loading animation
document.addEventListener('DOMContentLoaded', () => {
    setActiveNavLink();
    
    const sections = document.querySelectorAll('.nutrition-card, .goal-card, .meal-planner-card');
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

